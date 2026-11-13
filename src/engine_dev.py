# Compact UCI chess engine (dev). Standard library only.
import sys, time

# 0x88
A1,H1,A8,H8 = 112,119,0,7
N,E,S,W = -16,1,16,-1
dirs = {
 1:[N,N+E,E,S+E,S,S+W,W,N+W], # K (also used for neighbors)
 2:[2*N+E,2*N+W,2*E+N,2*E+S,2*S+E,2*S+W,2*W+N,2*W+S], # N
 3:[N+E,S+E,S+W,N+W], # B
 4:[N,E,S,W], # R
 5:[N,E,S,W,N+E,S+E,S+W,N+W], # Q
 6:[N,E,S,W,N+E,S+E,S+W,N+W], # p? no
}
# piece types: 1 P,2 N,3 B,4 R,5 Q,6 K
slider = {3:1,4:1,5:1}
vals = [0,100,320,330,500,900,20000]

# simple PST (middlegame-ish), from white perspective, indexed by 0x88 square 0..127
def mkpst():
    p=[0]*128
    # pawns
    pp=[0,5,5,0,5,10,20,0,0,10,15,20,20,15,10,0,5,10,15,25,25,15,10,5,10,15,20,30,30,20,15,10,20,25,30,35,35,30,25,20,50,50,50,50,50,50,50,50,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    n=[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50]
    b=[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20]
    r=[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0]
    q=[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20]
    k=[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]
    tabs=[None,pp,n,b,r,q,k]
    return tabs
PST = mkpst()

MATE=30000

class Pos:
    __slots__=('b','c','ep','ca','hm','hist','ks')
    def __init__(self):
        self.b=[0]*128
        self.c=1 # 1 white, -1 black
        self.ep=-1
        self.ca=[1,1,1,1] # KQkq
        self.hm=0
        self.hist=[]
        self.ks={1:116,-1:4}
    def copy(self):
        p=Pos(); p.b=self.b[:]; p.c=self.c; p.ep=self.ep; p.ca=self.ca[:]; p.hm=self.hm; p.ks=self.ks.copy(); return p

def on(i): return i&0x88==0
def rc(i): return i>>4, i&7

def set_fen(pos,fen):
    pos.b=[0]*128; pos.ks={}
    parts=fen.split()
    board=parts[0]
    r=0; f=0
    for ch in board:
        if ch=='/': r+=1; f=0
        elif ch.isdigit(): f+=int(ch)
        else:
            pt='PNBRQKpnbrqk'.index(ch)
            p=(pt%6)+1
            col=1 if pt<6 else -1
            i=r*16+f
            pos.b[i]=col*p
            if p==6: pos.ks[col]=i
            f+=1
    pos.c=1 if (len(parts)>1 and parts[1]=='w') else -1
    pos.ca=[0,0,0,0]
    if len(parts)>2:
        s=parts[2]
        if 'K' in s: pos.ca[0]=1
        if 'Q' in s: pos.ca[1]=1
        if 'k' in s: pos.ca[2]=1
        if 'q' in s: pos.ca[3]=1
    pos.ep=-1
    if len(parts)>3 and parts[3]!='-':
        f=ord(parts[3][0])-97; r8=8-int(parts[3][1]); pos.ep=r8*16+f
    pos.hm=int(parts[4]) if len(parts)>4 else 0

def sq_name(i): return 'abcdefgh'[i&7]+str(8-(i>>4))

def parse_sq(s): return (8-int(s[1]))*16+(ord(s[0])-97)

def attacked(pos,i,by):
    b=pos.b
    # pawns
    if by==1:
        for d in (S+W,S+E):
            j=i+d
            if on(j) and b[j]==1: return True
    else:
        for d in (N+W,N+E):
            j=i+d
            if on(j) and b[j]==-1: return True
    # knights
    for d in dirs[2]:
        j=i+d
        if on(j) and b[j]==2*by: return True
    # sliders/king
    for p,ds in ((3,dirs[3]),(4,dirs[4]),(5,dirs[5]),(6,dirs[1])):
        for d in ds:
            j=i+d
            while on(j):
                v=b[j]
                if v:
                    if v==p*by or (p==6 and v==6*by): return True
                    break
                if p==6 or p==2: break
                j+=d
    return False

def in_check(pos,c):
    k=pos.ks.get(c)
    if k is None: return True
    return attacked(pos,k,-c)

def gen_moves(pos):
    b=pos.b; c=pos.c; ms=[]
    for i in range(128):
        if not on(i): continue
        v=b[i]
        if v*c<=0: continue
        p=abs(v)
        if p==1:
            d=-16*c; j=i+d
            if on(j) and b[j]==0:
                if (j>>4)==(0 if c==1 else 7):
                    for pr in (5,4,3,2): ms.append((i,j,pr))
                else:
                    ms.append((i,j,0))
                    j2=i+2*d
                    if (i>>4)==(6 if c==1 else 1) and b[j2]==0: ms.append((i,j2,0))
            for dd in (d+W,d+E):
                j=i+dd
                if on(j) and b[j]*c<0:
                    if (j>>4)==(0 if c==1 else 7):
                        for pr in (5,4,3,2): ms.append((i,j,pr))
                    else: ms.append((i,j,0))
                elif j==pos.ep: ms.append((i,j,-1)) # ep mark
        elif p==2:
            for d in dirs[2]:
                j=i+d
                if on(j) and b[j]*c<=0: ms.append((i,j,0))
        elif p==6:
            for d in dirs[1]:
                j=i+d
                if on(j) and b[j]*c<=0: ms.append((i,j,0))
            # castle
            if c==1 and i==116 and not in_check(pos,1):
                if pos.ca[0] and b[117]==0 and b[118]==0 and not attacked(pos,117,-1) and not attacked(pos,118,-1): ms.append((116,118,9))
                if pos.ca[1] and b[115]==0 and b[114]==0 and b[113]==0 and not attacked(pos,115,-1) and not attacked(pos,114,-1): ms.append((116,114,9))
            if c==-1 and i==4 and not in_check(pos,-1):
                if pos.ca[2] and b[5]==0 and b[6]==0 and not attacked(pos,5,1) and not attacked(pos,6,1): ms.append((4,6,9))
                if pos.ca[3] and b[3]==0 and b[2]==0 and b[1]==0 and not attacked(pos,3,1) and not attacked(pos,2,1): ms.append((4,2,9))
        else:
            ds=dirs[5] if p==5 else (dirs[3] if p==3 else dirs[4])
            for d in ds:
                j=i+d
                while on(j):
                    if b[j]*c<=0: ms.append((i,j,0))
                    if b[j]!=0: break
                    j+=d
    return ms

def make(pos,m):
    i,j,pr=m
    b=pos.b; c=pos.c
    st=(b[i],b[j],pos.ep,pos.ca[:],pos.hm,pos.ks.copy())
    p=abs(b[i])
    pos.hm = 0 if p==1 or b[j]!=0 else pos.hm+1
    pos.ep=-1
    # en passant capture
    if pr==-1:
        cap=j+(16*c)
        b[cap]=0
    # move
    b[j]=b[i]; b[i]=0
    # promotion
    if pr>0 and pr!=9:
        b[j]=c*pr
    # king move/castle
    if p==6:
        pos.ks[c]=j
        if pr==9:
            if j==118: b[117]=b[119]; b[119]=0
            elif j==114: b[115]=b[112]; b[112]=0
            elif j==6: b[5]=b[7]; b[7]=0
            elif j==2: b[3]=b[0]; b[0]=0
        if c==1: pos.ca[0]=pos.ca[1]=0
        else: pos.ca[2]=pos.ca[3]=0
    # rook moves affect castling
    for sq,idx in ((112,1),(119,0),(0,3),(7,2)):
        if i==sq or j==sq: pos.ca[idx]=0
    # double pawn push
    if p==1 and abs(j-i)==32:
        pos.ep=(i+j)//2
    pos.c=-c
    return st

def unmake(pos,m,st):
    i,j,pr=m
    b[pos.i if False else 0] # dummy
    pos.b[i],pos.b[j],pos.ep,pos.ca,pos.hm,pos.ks = st[0],st[1],st[2],st[3],st[4],st[5]
    # but easier: restore from saved
    # rebuild carefully
    pass

# simpler make/unmake using saved snapshot of changed squares
def make2(pos,m):
    i,j,pr=m; b=pos.b; c=pos.c
    st=(i,j,pr,b[i],b[j],pos.ep,pos.ca[:],pos.hm,pos.ks.get(1),pos.ks.get(-1),None,None)
    # extra for ep capture or rook in castle
    extra=None
    p=abs(b[i])
    pos.hm = 0 if p==1 or b[j]!=0 else pos.hm+1
    pos.ep=-1
    if pr==-1:
        cap=j+16*c; extra=(cap,b[cap]); b[cap]=0
    b[j]=b[i]; b[i]=0
    if pr>0 and pr!=9:
        b[j]=c*pr
    if p==6:
        pos.ks[c]=j
        if pr==9:
            if j==118: extra=(119,117,b[119],b[117]); b[117]=b[119]; b[119]=0
            elif j==114: extra=(112,115,b[112],b[115]); b[115]=b[112]; b[112]=0
            elif j==6: extra=(7,5,b[7],b[5]); b[5]=b[7]; b[7]=0
            elif j==2: extra=(0,3,b[0],b[3]); b[3]=b[0]; b[0]=0
        if c==1: pos.ca[0]=pos.ca[1]=0
        else: pos.ca[2]=pos.ca[3]=0
    for sq,idx in ((112,1),(119,0),(0,3),(7,2)):
        if i==sq or j==sq: pos.ca[idx]=0
    if p==1 and abs(j-i)==32:
        pos.ep=(i+j)//2
    pos.c=-c
    return (st,extra)

def unmake2(pos,rec):
    st,extra=rec
    i,j,pr,bi,bj,ep,ca,hm,k1,km1,_,_=st
    b=pos.b
    pos.c=-pos.c
    b[i]=bi; b[j]=bj
    pos.ep=ep; pos.ca=ca; pos.hm=hm
    if k1 is not None: pos.ks[1]=k1
    if km1 is not None: pos.ks[-1]=km1
    if extra:
        if pr==9:
            a,b2,va,vb=extra; b[a]=va; b[b2]=vb
        elif pr==-1:
            cap,v=extra; b[cap]=v

def legal_moves(pos):
    ms=[]
    c=pos.c
    for m in gen_moves(pos):
        rec=make2(pos,m)
        if not in_check(pos,c): ms.append(m)
        unmake2(pos,rec)
    return ms

def eval_pos(pos):
    sc=0
    b=pos.b
    for i in range(128):
        if not on(i): continue
        v=b[i]
        if v==0: continue
        p=abs(v); c=1 if v>0 else -1
        val=vals[p]
        pst=PST[p]
        sq=(i>>4)*8 + (i&7)
        idx = sq if c==1 else (56 - (i>>4)*8 + (i&7))
        val += pst[idx] if p!=6 else (pst[idx]//2)
        sc += c*val
    return sc if pos.c==1 else -sc

def move_to_str(m):
    i,j,pr=m
    s=sq_name(i)+sq_name(j)
    if pr>0 and pr!=9:
        s += ' nbrq'[pr]
    return s

def parse_move(pos,s):
    i=parse_sq(s[:2]); j=parse_sq(s[2:4])
    pr=0
    if len(s)>4:
        pr={'n':2,'b':3,'r':4,'q':5}[s[4]]
    # detect castle/ep by matching legal move
    for m in legal_moves(pos):
        if m[0]==i and m[1]==j:
            if pr and m[2]==pr: return m
            if not pr and m[2] in (0,-1,9): return m
            if pr==0 and m[2]==5 and len(s)==4: # default? not expected
                return m
    # fallback
    for m in legal_moves(pos):
        if m[0]==i and m[1]==j: return m
    return (i,j,pr)

nodes=0; stop_time=0; stop_flag=False

def qsearch(pos,a,b):
    global nodes, stop_flag
    nodes+=1
    sc=eval_pos(pos)
    if sc>=b: return b
    if sc>a: a=sc
    # captures/promotions only
    ms=legal_moves(pos)
    caps=[m for m in ms if pos.b[m[1]]!=0 or m[2]>0]
    for m in caps:
        rec=make2(pos,m)
        v=-qsearch(pos,-b,-a)
        unmake2(pos,rec)
        if v>=b: return b
        if v>a: a=v
    return a

def search(pos,d,a,b,ply):
    global nodes, stop_time, stop_flag
    if nodes&1023==0 and time.time()>=stop_time: stop_flag=True
    if stop_flag: return 0
    if d<=0: return qsearch(pos,a,b)
    ms=legal_moves(pos)
    if not ms:
        if in_check(pos,pos.c): return -MATE+ply
        return 0
    # move ordering: captures/promotions first
    def key(m):
        t=pos.b[m[1]]
        return (10 if t else 0) + (abs(t) if t else 0) + (m[2] if m[2]>0 else 0)
    ms.sort(key=key, reverse=True)
    best=-MATE
    for m in ms:
        rec=make2(pos,m)
        v=-search(pos,d-1,-b,-a,ply+1)
        unmake2(pos,rec)
        if stop_flag: return 0
        if v>best: best=v
        if v>a: a=v
        if a>=b: break
    return best

def best_move(pos, tlim):
    global nodes, stop_time, stop_flag
    stop_time=time.time()+tlim
    stop_flag=False
    ms=legal_moves(pos)
    if not ms: return None
    bm=ms[0]
    for d in range(1,64):
        nodes=0
        best=-MATE; cur=bm
        a,b=-MATE,MATE
        # root search
        ms2=legal_moves(pos)
        def key(m): t=pos.b[m[1]]; return (10 if t else 0)+(abs(t) if t else 0)+(m[2] if m[2]>0 else 0)
        ms2.sort(key=key, reverse=True)
        for m in ms2:
            rec=make2(pos,m)
            v=-search(pos,d-1,-b,-a,1)
            unmake2(pos,rec)
            if stop_flag: break
            if v>best: best=v; cur=m
            if v>a: a=v
        if not stop_flag: bm=cur
        if stop_flag or time.time()>=stop_time: break
    return bm

def main():
    pos=Pos()
    set_fen(pos,'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        if line=='uci':
            print('id name C4K\nid author Hermes\nuciok', flush=True)
        elif line=='isready':
            print('readyok', flush=True)
        elif line.startswith('ucinewgame'):
            pos=Pos(); set_fen(pos,'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        elif line.startswith('position'):
            parts=line.split()
            idx=1
            if parts[idx]=='startpos':
                pos=Pos(); set_fen(pos,'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'); idx+=1
            elif parts[idx]=='fen':
                fen=' '.join(parts[idx+1:idx+7]); pos=Pos(); set_fen(pos,fen); idx+=7
            if idx<len(parts) and parts[idx]=='moves':
                for mv in parts[idx+1:]:
                    m=parse_move(pos,mv); make2(pos,m)
        elif line.startswith('go'):
            parts=line.split(); t=1.0
            if 'movetime' in parts: t=int(parts[parts.index('movetime')+1])/1000.0
            elif 'wtime' in parts and 'btime' in parts:
                wt=int(parts[parts.index('wtime')+1]); bt=int(parts[parts.index('btime')+1])
                wi=int(parts[parts.index('winc')+1]) if 'winc' in parts else 0
                bi=int(parts[parts.index('binc')+1]) if 'binc' in parts else 0
                rem=wt if pos.c==1 else bt; inc=wi if pos.c==1 else bi
                t=max(0.05, min(rem/1000.0/30.0 + inc/1000.0*0.8, rem/1000.0-0.1))
            bm=best_move(pos,t)
            if bm: print('bestmove', move_to_str(bm), flush=True)
            else: print('bestmove 0000', flush=True)
        elif line=='stop':
            pass
        elif line=='quit':
            break

if __name__=='__main__':
    main()
