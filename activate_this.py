# Protected by TRIPLER VIP ENCODER v1.0
# Owner: @YaminOnFire07
# Web: tynex_of.ff90.top
import marshal, zlib, base64

guardfcf268 = lambda _x: ''.join([chr(ord(_c) ^ 0) for _c in str(_x)])
if guardfcf268('tripler_sec') != 'tripler_sec':
    exit()

key26fa4c = [120, 168, 49, 219, 185, 143, 76, 39]
b8535cf25 = b'b3+3F001<+kM!V|A7~ZAjI|rjg0B7t1M+SzD7lL2-(*z^&2ELgTN!HI<1UIcNy{uVm^<RXzSe?>AmR4{C|^R?uG&BcsLP;G<tDP`QL|c7RTYR@R`_ZR4gU@RlV-Lrl@=U8yW?6o+D{E0v^}IRa57^;g4j)zy{<So-r@_I#dg-Da~WJ=^VQwY(@~w%f(`m4Yg5zZ@<4tiPtR|LG$iwwbs~RwLR2CXTau04zzgviw#nQFOtE#nH_|2u5)<;IN(dYl8c9AXhPr4q%pxnT7%2lBGg1_Q^swbOe<4A^zGPlUK*EtSAu!_8354zbi1y9~VELji^?|@t86R*7gE5t(t6BE6ehoa5WEG<WRR;hiK1)>3>3rTiNBoSUfYM$x+ga*;g{p`3by#k>?*|+zqw3zfD}4w^HO{@~e2BA=>lyA%9I90VHQ;IdNZwUBRA3-qPWU9}8kWvCsGTk-Z+!RghGaKFanD0a`$(6?F;t?WP8b_YYAK}sM~{*m_Ag`p)MniZ$Ixu!vkV6CT8!Lvw+O~FPti(z6T=U6D&wDk)NP7^(Nh7@GnJy8;>BwipXeQyf$D}2;rGv~ni-l@lyHW^h<7L2^bT;ooV|ZB{AtSoE9$JCl4~~IVlkTQF@*IX;EaX{I1)&yfUT0rNA(ZfI5JBTUt@O()lz<TVvjZLd&dXfOfqz-fJ0(QdMx0J41gp*ji#`?nC~M_#fN_!2Hzo?chmSZ@esQ@7Iv+l4exCkz=LeDMkq^piWs+26$$kCb{=(!W}GvTG|F)oDBnE`9$}cl-fH#13eH`{UAFYijq&Ibfp1l!{|P;`ok-7zMZrFos-Z3LWuHbB2i7DxhWk3ah%)6;d!Q*T7;(b=kr*rCJ~eI(d_$Yf9;XQfOZ(A9)QXQ@g+&~An%+$T@<ziWN!C>%K#Z-o4ssl#Bu-DTaxz;zN32ookGjkYj(cD1IVn0d;5M&m351ty9z?H>YnPb6fi6IjV%fWx#)VRC=@VQI#-xP{G#_&dS;Ma?6pzhF0yLNCtj}+{<X<djy&P8aJbz|%u(z)+CSR@QRCupy1fXMcYlJy9'

marshf58e28 = marshal.loads(base64.b85decode(b8535cf25))
dec9c8e4e = bytearray()
for _i, _b in enumerate(marshf58e28):
    dec9c8e4e.append(_b ^ key26fa4c[_i % len(key26fa4c)])

zlib4a6843 = zlib.decompress(bytes(dec9c8e4e)).decode('utf-8')
exec(compile(zlib4a6843, '<protected_by_owner>', 'exec'))
