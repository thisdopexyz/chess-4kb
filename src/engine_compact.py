import sys,time
M=30000;A1,H1=112,119
V=[0,100,320,330,500,900,0]
# PST 64 each
PST=[
[0]*64,
[0,5,5,0,5,10,20,0,0,10,15,20,20,15,10,0,5,10,15,25,25,15,10,5,10,15,20,30,30,20,15,10,20,25,30,35,35,30,25,20,50,50,50,50,50,50,50,50,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20],
]
D={2:[-33,-31,-18,-14,14,18,31,33],3:[-17,-15,15,17],4:[-16,-1,1,16],5:[-17,-16,-15,-1,1,15,16,17],6:[-17,-16,-15,-1,1,15,16,17]}
SL={3,4,5}
def on(i):return i&0x88==0
def sn(i):return 'abcdefgh'[i&7]+str(8-(i>>4))
def ps(s):return (8-int(s[1]))*16+(ord(s[0])-97)
def init():
    b=[0]*128;ca=[1,1,1,1];ep=-1;c=1;ks={1:116,-1:4}
    fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
    r=f=0
    for ch in fen:
        if ch=='/':r+=1;f=0
        elif ch.isdigit():f+=int(ch)
        else:
            t='PNBRQKpnbrqk'.index(ch);p=t%6+1;co=1 if t<6 else -1;i=r*16+f;b[i]=co*p
            if p==6:ks[co]=i
            f+=1
    return b,c,ep,ca,ks,0
def setfen(parts):
    b=[0]*128;ca=[0,0,0,0];ep=-1;c=1;ks={}
    r=f=0
    for ch in parts[0]:
        if ch=='/':r+=1;f=0
        elif ch.isdigit():f+=int(ch)
        else:
            t='PNBRQKpnbrqk'.index(ch);p=t%6+1;co=1 if t<6 else -1;i=r*16+f;b[i]=co*p
            if p==6:ks[co]=i
            f+=1
    c=1 if len(parts)>1 and parts[1]=='w' else -1
    if len(parts)>2:
        s=parts[2];ca=[1 if 'K' in s else 0,1 if 'Q' in s else 0,1 if 'k' in s else 0,1 if 'q' in s else 0]
    if len(parts)>3 and parts[3]!='-':ep=ps(parts[3])
    hm=int(parts[4]) if len(parts)>4 else 0
    return b,c,ep,ca,ks,hm
def atk(b,i,by):
    if by==1:
        for d in (15,17):
            j=i+d
            if on(j) and b[j]==1:return 1
    else:
        for d in (-17,-15):
            j=i+d
            if on(j) and b[j]==-1:return 1
    for d in D[2]:
        j=i+d
        if on(j) and b[j]==2*by:return 1
    for p,ds in ((3,D[3]),(4,D[4]),(5,D[5]),(6,D[6])):
        for d in ds:
            j=i+d
            while on(j):
                v=b[j]
                if v:
                    if v==p*by:return 1
                    break
                if p==6:break
                j+=d
    return 0
def inchk(b,c,ks):return atk(b,ks[c],-c)
def gen(b,c,ep,ca,ks):
    ms=[]
    for i in range(128):
        if not on(i):continue
        v=b[i]
        if v*c<=0:continue
        p=abs(v)
        if p==1:
            d=-16*c;j=i+d
            if on(j) and b[j]==0:
                if j>>4==(0 if c==1 else 7):
                    for pr in (5,4,3,2):ms.append((i,j,pr))
                else:
                    ms.append((i,j,0));j2=i+2*d
                    if i>>4==(6 if c==1 else 1) and b[j2]==0:ms.append((i,j2,0))
            for dd in (d-1,d+1):
                j=i+dd
                if on(j) and b[j]*c<0:
                    if j>>4==(0 if c==1 else 7):
                        for pr in (5,4,3,2):ms.append((i,j,pr))
                    else:ms.append((i,j,0))
                elif j==ep:ms.append((i,j,-1))
        elif p==2:
            for d in D[2]:
                j=i+d
                if on(j) and b[j]*c<=0:ms.append((i,j,0))
        elif p==6:
            for d in D[6]:
                j=i+d
                if on(j) and b[j]*c<=0:ms.append((i,j,0))
            if c==1 and i==116 and not inchk(b,1,ks):
                if ca[0] and b[117]==0 and b[118]==0 and not atk(b,117,-1) and not atk(b,118,-1):ms.append((116,118,9))
                if ca[1] and b[115]==0 and b[114]==0 and b[113]==0 and not atk(b,115,-1) and not atk(b,114,-1):ms.append((116,114,9))
            if c==-1 and i==4 and not inchk(b,-1,ks):
                if ca[2] and b[5]==0 and b[6]==0 and not atk(b,5,1) and not atk(b,6,1):ms.append((4,6,9))
                if ca[3] and b[3]==0 and b[2]==0 and b[1]==0 and not atk(b,3,1) and not atk(b,2,1):ms.append((4,2,9))
        else:
            for d in D[p]:
                j=i+d
                while on(j):
                    if b[j]*c<=0:ms.append((i,j,0))
                    if b[j]!=0:break
                    j+=d
    return ms
def mk(b,c,ep,ca,ks,hm,m):
    i,j,pr=m;st=(i,j,pr,b[i],b[j],ep,ca[:],hm,ks[1],ks[-1]);ex=None;p=abs(b[i])
    hm=0 if p==1 or b[j]!=0 else hm+1;ep=-1
    if pr==-1:cap=j+16*c;ex=(cap,b[cap]);b[cap]=0
    b[j]=b[i];b[i]=0
    if pr>0 and pr!=9:b[j]=c*pr
    if p==6:
        ks[c]=j
        if pr==9:
            if j==118:ex=(119,117,b[119],b[117]);b[117]=b[119];b[119]=0
            elif j==114:ex=(112,115,b[112],b[115]);b[115]=b[112];b[112]=0
            elif j==6:ex=(7,5,b[7],b[5]);b[5]=b[7];b[7]=0
            elif j==2:ex=(0,3,b[0],b[3]);b[3]=b[0];b[0]=0
        if c==1:ca[0]=ca[1]=0
        else:ca[2]=ca[3]=0
    for sq,x in ((112,1),(119,0),(0,3),(7,2)):
        if i==sq or j==sq:ca[x]=0
    if p==1 and abs(j-i)==32:ep=(i+j)//2
    return (st,ex),-c,ep,ca,ks,hm
def um(b,c,ep,ca,ks,hm,rec):
    st,ex=rec;i,j,pr,bi,bj,ep2,ca2,hm2,k1,km1=st
    b[i]=bi;b[j]=bj;ks[1]=k1;ks[-1]=km1
    if ex:
        if pr==9:a,d,va,vd=ex;b[a]=va;b[d]=vd
        elif pr==-1:cap,v=ex;b[cap]=v
    return -c,ep2,ca2,ks,hm2
def legal(b,c,ep,ca,ks,hm):
    out=[]
    for m in gen(b,c,ep,ca,ks):
        rec,c2,ep2,ca2,ks2,hm2=mk(b,c,ep,ca,ks,hm,m)
        if not inchk(b,c,ks):out.append(m)
        c,ep,ca,ks,hm=um(b,c2,ep2,ca2,ks2,hm2,rec)
    return out
def ev(b,c):
    sc=0
    for i in range(128):
        if not on(i):continue
        v=b[i]
        if not v:continue
        p=abs(v);co=1 if v>0 else -1;sq=(i>>4)*8+(i&7);idx=sq if co==1 else 56-(i>>4)*8+(i&7)
        s=V[p]+PST[p][idx]
        sc+=co*s
    return sc if c==1 else -sc
NODES=0;TEND=0;STOP=0
def qs(b,c,ep,ca,ks,hm,a,be):
    global NODES
    NODES+=1;sc=ev(b,c)
    if sc>=be:return be
    if sc>a:a=sc
    ms=legal(b,c,ep,ca,ks,hm)
    for m in ms:
        if b[m[1]]==0 and m[2]<=0:continue
        rec,c2,ep2,ca2,ks2,hm2=mk(b,c,ep,ca,ks,hm,m)
        v=-qs(b,c2,ep2,ca2,ks2,hm2,-be,-a)
        c,ep,ca,ks,hm=um(b,c2,ep2,ca2,ks2,hm2,rec)
        if v>=be:return be
        if v>a:a=v
    return a
def sr(b,c,ep,ca,ks,hm,d,a,be,ply):
    global NODES,TEND,STOP
    if NODES&1023==0 and time.time()>=TEND:STOP=1
    if STOP:return 0
    if d<=0:return qs(b,c,ep,ca,ks,hm,a,be)
    ms=legal(b,c,ep,ca,ks,hm)
    if not ms:return 0 if not inchk(b,c,ks) else -M+ply
    ms.sort(key=lambda m:(10 if b[m[1]] else 0)+abs(b[m[1]])+(m[2] if m[2]>0 else 0),reverse=True)
    best=-M
    for m in ms:
        rec,c2,ep2,ca2,ks2,hm2=mk(b,c,ep,ca,ks,hm,m)
        v=-sr(b,c2,ep2,ca2,ks2,hm2,d-1,-be,-a,ply+1)
        c,ep,ca,ks,hm=um(b,c2,ep2,ca2,ks2,hm2,rec)
        if STOP:return 0
        if v>best:best=v
        if v>a:a=v
        if a>=be:break
    return best
def best(b,c,ep,ca,ks,hm,tlim):
    global NODES,TEND,STOP
    TEND=time.time()+tlim;STOP=0
    ms=legal(b,c,ep,ca,ks,hm)
    if not ms:return None
    bm=ms[0]
    for d in range(1,50):
        NODES=0;a,be=-M,M;cur=bm;loc=-M
        ms2=legal(b,c,ep,ca,ks,hm)
        ms2.sort(key=lambda m:(10 if b[m[1]] else 0)+abs(b[m[1]])+(m[2] if m[2]>0 else 0),reverse=True)
        for m in ms2:
            rec,c2,ep2,ca2,ks2,hm2=mk(b,c,ep,ca,ks,hm,m)
            v=-sr(b,c2,ep2,ca2,ks2,hm2,d-1,-be,-a,1)
            c,ep,ca,ks,hm=um(b,c2,ep2,ca2,ks2,hm2,rec)
            if STOP:break
            if v>loc:loc=v;cur=m
            if v>a:a=v
        if not STOP:bm=cur
        if STOP or time.time()>=TEND:break
    return bm
def mts(m):
    i,j,pr=m;s=sn(i)+sn(j)
    if pr>0 and pr!=9:s+=' nbrq'[pr]
    return s
def pm(b,c,ep,ca,ks,hm,s):
    i=ps(s[:2]);j=ps(s[2:4]);pr=0
    if len(s)>4:pr={'n':2,'b':3,'r':4,'q':5}[s[4]]
    for m in legal(b,c,ep,ca,ks,hm):
        if m[0]==i and m[1]==j and (pr==m[2] or (not pr and m[2] in (0,-1,9))):return m
    for m in legal(b,c,ep,ca,ks,hm):
        if m[0]==i and m[1]==j:return m
    return (i,j,pr)
def main():
    b,c,ep,ca,ks,hm=init()
    for line in sys.stdin:
        line=line.strip()
        if not line:continue
        if line=='uci':print('id name C4K\nid author Hermes\nuciok',flush=True)
        elif line=='isready':print('readyok',flush=True)
        elif line.startswith('ucinewgame'):b,c,ep,ca,ks,hm=init()
        elif line.startswith('position'):
            parts=line.split();k=1
            if parts[k]=='startpos':b,c,ep,ca,ks,hm=init();k+=1
            elif parts[k]=='fen':b,c,ep,ca,ks,hm=setfen(parts[k+1:k+7]);k+=7
            if k<len(parts) and parts[k]=='moves':
                for mv in parts[k+1:]:
                    m=pm(b,c,ep,ca,ks,hm,mv);_,c,ep,ca,ks,hm=mk(b,c,ep,ca,ks,hm,m)
        elif line.startswith('go'):
            parts=line.split();t=0.5
            if 'movetime' in parts:t=int(parts[parts.index('movetime')+1])/1000
            elif 'wtime' in parts and 'btime' in parts:
                wt=int(parts[parts.index('wtime')+1]);bt=int(parts[parts.index('btime')+1])
                wi=int(parts[parts.index('winc')+1]) if 'winc' in parts else 0
                bi=int(parts[parts.index('binc')+1]) if 'binc' in parts else 0
                rem=wt if c==1 else bt;inc=wi if c==1 else bi
                t=max(0.05,min(rem/30000+inc/1250,rem/1000-0.1))
            bm=best(b,c,ep,ca,ks,hm,t)
            print('bestmove',mts(bm) if bm else '0000',flush=True)
        elif line=='quit':break
if __name__=='__main__':main()
