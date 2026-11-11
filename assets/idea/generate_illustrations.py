"""Regenerate the three illustrations embedded in ../../idea.md (requires Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT = Path(__file__).resolve().parent
S = 2
INK, MUTED, LINE = '#18334B', '#62758A', '#D8E2EC'
BLUE, TEAL, AMBER = '#386BDB', '#16877D', '#B47A25'
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'

class Canvas:
    def __init__(self, title, subtitle, height=740):
        self.im = Image.new('RGB', (1280*S, height*S), '#F5F8FC')
        self.d = ImageDraw.Draw(self.im)
        self.text(48, 34, title, 30, INK)
        self.text(48, 84, subtitle, 17, MUTED)
    def text(self, x, y, text, size=20, color=INK, center=False):
        f = ImageFont.truetype(FONT, size*S)
        self.d.text((x*S, y*S), text, font=f, fill=color, anchor='mt' if center else 'lt')
    def box(self, x, y, w, h, title, lines=(), color=BLUE, fill='#FFFFFF'):
        self.d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S), radius=16*S, fill=fill, outline=LINE, width=1*S)
        self.d.rounded_rectangle(((x+18)*S,(y+20)*S,(x+23)*S,(y+46)*S),radius=2*S,fill=color)
        self.text(x+36,y+21,title,22,color)
        for i,t in enumerate(lines): self.text(x+22,y+66+i*29,t,17,MUTED)
    def arrow(self, pts, color=BLUE, width=3):
        p = [(int(x*S),int(y*S)) for x,y in pts]
        self.d.line(p,fill=color,width=width*S,joint='curve')
        x,y=p[-1]; a=math.atan2(y-p[-2][1], x-p[-2][0]); n=10*S
        self.d.polygon([(x,y),(x-n*math.cos(a-.45),y-n*math.sin(a-.45)),(x-n*math.cos(a+.45),y-n*math.sin(a+.45))],fill=color)
    def note(self, y, text):
        self.text(48,y,text,17,MUTED)
    def save(self, name):
        self.im.save(OUT/name, optimize=True)

c=Canvas('从权威规格到可验证代码', 'DAG 任务分解示意 · 箭头表示依赖关系，节点对应可独立生成和验证的代码单元', 760)
c.box(48,160,248,174,'规格源', ['CCDD / 可选 EDS','命令 · 遥测 · 消息','表格配置'],TEAL)
c.box(350,160,300,174,'应用骨架规划',['源文件 · 头文件 · 表格','CMake 条目','模板 + 数据驱动生成'])
c.box(726,160,506,174,'接口层规划',['Software Bus 初始化与消息映射','消息 ID · 收发调用模式','模板 + CCDD 消息映射'])
c.box(726,410,506,174,'逻辑层规划',['AppMain：命令分发 · 遥测 · 表格处理','处理函数体：LLM 在预设规则内生成','错误处理：组合代码片段'],TEAL)
c.box(350,410,300,174,'逐单元验证',['编译 · 单测 · 静态检查','失败信息回传生成层','功能测试冒烟'],TEAL)
c.arrow([(296,247),(350,247)])
c.arrow([(650,247),(726,247)])
c.arrow([(978,334),(978,410)])
c.arrow([(726,497),(650,497)],TEAL)
c.note(650,'生成分工：骨架与接口确定性生成；业务逻辑在预设代码模式和安全规则内生成。')
c.note(688,'流程依据原文绘制，表达规划关系；具体节点和依赖由应用需求决定。')
c.save('01-spec-to-dag.png')

c=Canvas('生成—验证：有界反馈闭环','验证是生成循环的一部分 · 失败信息以结构化形式回传',760)
c.box(48,170,230,174,'生成 / 修正',['模板 + CCDD','受约束的业务逻辑','生成对应单测'])
c.box(330,170,230,174,'编译验证',['pc-linux 环境','容器内构建','编译错误定位'])
c.box(612,170,278,174,'单测 / 静态检查',['执行单元测试','CodeQL / Cppcheck','规则检查'])
c.box(942,170,290,174,'功能测试冒烟',['运行 cFS 实例','发送命令 · 验证遥测','通过 → 完成本轮验证'],TEAL)
for a,b in [(278,330),(560,612),(890,942)]: c.arrow([(a,257),(b,257)])
c.box(330,456,560,120,'失败反馈 → 修正 → 重新验证',['结构化错误信息 · 错误定位 · 受限重试'],AMBER, '#FFFBF3')
c.arrow([(751,344),(751,405),(610,405),(610,456)],AMBER)
c.arrow([(445,344),(445,405),(610,405)],AMBER)
c.arrow([(1087,344),(1087,405),(751,405)],AMBER)
c.arrow([(330,516),(163,516),(163,344)],AMBER)
c.box(942,456,290,120,'达到迭代上限',['例如 3 轮 → 人工介入'],AMBER,'#FFFBF3')
c.arrow([(890,516),(942,516)],AMBER)
c.note(654,'蓝色：生成与验证主流程     绿色：通过验证     琥珀色：失败反馈与迭代边界')
c.note(692,'上限必须硬性限制；超过上限后输出“需要人工介入”，避免无限重试。')
c.save('02-validation-loop.png')

c=Canvas('双角色协作：共享事实，隔离上下文','内核级双角色架构示意 · Generator 生成，Verifier 验证',850)
c.box(48,165,474,200,'Generator Agent',['调用生成类工具，产生代码','独立历史：生成尝试 · 修正记录','写入范围：apps/<app_name>/'])
c.box(758,165,474,200,'Verifier Agent',['调用构建 · 单测 · 静态检查工具','独立上下文：待验证产物 + 验证规则','返回：通过 / 失败 + 错误定位'],TEAL)
c.arrow([(522,225),(758,225)])
c.text(640,193,'路径 + 变更摘要',15,BLUE,True)
c.arrow([(758,307),(522,307)],TEAL)
c.text(640,323,'结构化验证结果',15,TEAL,True)
c.box(48,466,1184,130,'共享事实层',['CCDD 解析缓存     ·     容器句柄     ·     文件系统状态'],TEAL,'#EBF7F4')
c.arrow([(285,466),(285,365)],TEAL)
c.arrow([(995,466),(995,365)],TEAL)
c.box(48,644,1184,104,'策略与执行边界',['规格源只读     ·     核心目录受保护     ·     构建进入容器     ·     生成—验证有界循环'],AMBER,'#FFFBF3')
c.note(791,'共享同一份工程事实；生成历史与验证上下文分别维护。')
c.save('03-agent-architecture.png')
