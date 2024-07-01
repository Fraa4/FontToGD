from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from collections import defaultdict
import math
from gzip import compress
from base64 import urlsafe_b64encode

num2words = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 
             6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 0: "zero"}

def n2w(n):
    if n.isdecimal():
        i = int(n)
        return num2words[i]

with open("config.txt", "r") as cfg:
    conf = cfg.read().split("\n")
    ttf_path = str(conf[0][conf[0].find("[") + 1:conf[0].find("]")])
    scaleY = float(conf[1][conf[1].find("[") + 1:conf[1].find("]")])
    offset = float(conf[2][conf[2].find("[") + 1:conf[2].find("]")]) * 30
    div = 30 / float(conf[3][conf[3].find("[") + 1:conf[3].find("]")])
    corners = bool(int(conf[4][conf[4].find("[") + 1:conf[4].find("]")]))
    custext = str(conf[5][conf[5].find("[") + 1:conf[5].find("]")])
    print("Debug Log: " + ttf_path + " " + str(scaleY) + " " + str(offset) + " " + str(div) + " " + str(corners))

def CreateFile(s):
    lvlstr = compress(s.encode())
    lvlstr = urlsafe_b64encode(lvlstr)
    strin = "<d><k>kCEK</k><i>4</i><k>k18</k><i>43</i><k>k36</k><i>26</i><k>k85</k><i>48</i><k>k86</k><i>13</i><k>k87</k><i>908714</i><k>k88</k><s>99</s><k>k89</k><t/><k>k23</k><i>1</i><k>k19</k><i>99</i><k>k71</k><i>99</i><k>k90</k><i>99</i><k>k20</k><i>99</i><k>k2</k><s>Font</s><k>k4</k><s>"
    strlast = "</s><k>k5</k><s>Fra4</s><k>k95</k><i>1694</i><k>k101</k><s>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</s><k>k13</k><t/><k>k21</k><i>2</i><k>k16</k><i>1</i><k>k80</k><i>4013</i><k>k81</k><i>22811</i><k>k42</k><i>98711088</i><k>k45</k><i>76743</i><k>k50</k><i>39</i><k>k47</k><t/><k>k48</k><i>2271</i><k>k66</k><i>9</i><k>kI1</k><r>-2398.72</r><k>kI2</k><r>74.8316</r><k>kI3</k><r>0.1</r><k>kI5</k><i>9</i><k>kI6</k><d><k>0</k><s>0</s><k>1</k><s>0</s><k>2</k><s>2</s><k>3</k><s>0</s><k>4</k><s>0</s><k>5</k><s>0</s><k>6</k><s>0</s><k>7</k><s>0</s><k>8</k><s>0</s><k>9</k><s>0</s><k>10</k><s>6</s><k>11</k><s>0</s><k>12</k><s>0</s><k>13</k><s>0</s></d></d>"
    final = strin + lvlstr.decode() + strlast
    with open("level/level.gmd", "w") as fn:
        fn.write(final)
    print("Done")

def ConvertToGDLine(posX, posY, off):
    stGD = ""
    for a in range(1, len(posX), 1):
        if posX[a] - posX[a - 1] != 0:
            tan = (posY[a] - posY[a - 1]) / (posX[a] - posX[a - 1])
            rot = math.degrees(math.atan(tan))
        else:
            rot = 90
        mX = (posX[a] / div + posX[a - 1] / div) / 2
        mY = (posY[a] / div + posY[a - 1] / div) / 2

        scale = math.dist([posX[a - 1] / div, posY[a - 1] / div], [posX[a] / div, posY[a] / div]) / 30
        stGD += "1,1753,2," + str(mX + off) + ",3," + str(mY + 30) + ",6," + str(-rot) + ",128," + str(scale) + ",129," + str(scaleY) + ",21,1;"
        if corners:
            stGD += "1,1764,2," + str((posX[a]) / div + off) + ",3," + str(posY[a] / div + 30) + ",32," + str(scaleY / 8) + ",21,1;"
    return stGD

class GlyphPointsPen(BasePen):
    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.points = []

    def _moveTo(self, p0):
        self.points.append(('moveTo', p0))

    def _lineTo(self, p1):
        self.points.append(('lineTo', p1))

    def _qCurveToOne(self, p1, p2):
        self.points.append(('qCurveTo', p1, p2))

    def _curveToOne(self, p1, p2, p3):
        self.points.append(('curveTo', p1, p2, p3))

def extract_glyph_points(ttf_path):
    font = TTFont(ttf_path)
    glyph_set = font.getGlyphSet()
    cmap = font['cmap'].getBestCmap()
    glyph_points = {}

    for codepoint, glyph_name in cmap.items():
        glyph = glyph_set[glyph_name]
        pen = GlyphPointsPen(glyph_set)
        glyph.draw(pen)
        char = chr(codepoint)
        glyph_points[char] = pen.points

    font.close()
    return glyph_points

glyph_points = extract_glyph_points(ttf_path)

gdStr = ""
c = 0
off = 0
if(custext==""):
    for glyph_name, points in glyph_points.items():
        off+=offset
        c+=1
        posX = []
        posY = []
        if not points:
            continue  # Skip glyphs with no points
        startX=points[0][1][0]
        startY=points[0][1][1]
        print(f"Glyph: {glyph_name}")
        for point in points:
            if point[0] in ["lineTo", "qCurveTo", "curveTo"]:
                posX.append(point[1][0])
                posY.append(point[1][1])
            elif point[0] == "moveTo":
                if posX and posY:
                    posX.append(startX)
                    posY.append(startY)
                    startX=point[1][0]
                    startY=point[1][1]
                    gdStr+=ConvertToGDLine(posX,posY,off)
                    
                posX = [point[1][0]]
                posY = [point[1][1]]
            

        if posX and posY:
            posX.append(startX)
            posY.append(startY)
            gdStr+=ConvertToGDLine(posX,posY,off)
    CreateFile(gdStr)
else:
    for a in range(0,len(custext)):
        if(custext[a]==" "):
            off+=offset
        else:
            for glyph_name, points in glyph_points.items():
                if(glyph_name==custext[a] or glyph_name==n2w(custext[a])):
                    off+=offset
                    if not points:
                        continue  # Skip glyphs with no points
                    startX=points[0][1][0]
                    startY=points[0][1][1]
                    print(f"Glyph: {glyph_name}")
                    posX = []
                    posY = []
                    for point in points:
                        if point[0] in ["lineTo", "qCurveTo", "curveTo"]:
                            posX.append(point[1][0])
                            posY.append(point[1][1])
                        elif point[0] == "moveTo":
                            if posX and posY:
                                posX.append(startX)
                                posY.append(startY)
                                startX=point[1][0]
                                startY=point[1][1]
                                gdStr+=ConvertToGDLine(posX,posY,off)
                                
                            posX = [point[1][0]]
                            posY = [point[1][1]]
                    if posX and posY:
                        posX.append(startX)
                        posY.append(startY)
                        gdStr+=ConvertToGDLine(posX,posY,off)

    CreateFile(gdStr)
