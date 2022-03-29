from lark import Lark, Tree
from lark.visitors import Interpreter, visit_children_decor
from collections import deque

LYRIC_PARSER_GRAMMAR = r"""
%import common (CR, LF)

start : _ws part (_EOLS part)*
part : a_line (_EOL a_line)*
a_line : (elem_group _INL_WS?)* elem_group _inl_ws
?elem_group : (elem "_")* elem dash?

elem : WORD PIPES?
dash : "-"
_ws : _WS?
_inl_ws : _INL_WS*

WORD : CHAR+
CHAR : /[^\s_|-]/
PIPES : "|"+
_EOLS : /(:?\r?\n\s*){2,}/
_EOL: CR? LF
_INL_WS : " "
_WS : /\s+/
"""

class LyricCaptionExtractor(Interpreter):
    def __init__(self):
        self.line: str
        self.full_line: str
        self.dash_detected = False

    def _append_current(self):
        #print(self.line+'|')
        if hasattr(self, 'captions'):
            self.captions.append((self.line, self.full_line[len(self.line):]))

    def _add_then_append(self, text: str):
        self.line += text
        self._append_current()

    def extract(self, tree: Tree, text: str) -> 'deque[tuple[str, str]]':
        self.captions: deque[tuple[str, str]] = deque()
        self.lines = text.split('\n')
        self.visit(tree)
        ret = self.captions
        del self.captions
        return ret

    @visit_children_decor #type: ignore
    def start(self, t):
        self.__init__()

    def a_line(self, t):
        self.line = ''
        lineno = t.meta.line
        self.full_line = self.lines[lineno-1]
        size = len(t.children)
        i = 0
        for c in t.children:
            self.visit(c)
            i += 1
            if (i < size):
                self.line += '-' if self.dash_detected else ' '
                self.dash_detected = False

    def elem(self, t):
        elem = t.children[0]
        self._add_then_append(elem)
        try:
            pipes = t.children[1]
            for _ in range(len(pipes)):
                self._append_current()
        except IndexError:
            pass

    def dash(self, t):
        self.dash_detected = True


def lyric2captions(lyric: str) -> 'deque[tuple[str, str]]':
    parser = Lark(LYRIC_PARSER_GRAMMAR, parser='lalr', debug=True, propagate_positions=True, cache=True)
    tree = parser.parse(lyric)
    extractor = LyricCaptionExtractor()
    return extractor.extract(tree, text)

if __name__ == "__main__":
    import cProfile
    from pprint import pprint

    text = """
Em là ai từ đâu bước đến nơi đây dịu dàng chân phương
Em là ai tựa như ánh nắng ban mai ngọt ngào trong sương
Ngắm em thật lâu con tim anh yếu mềm
Đắm say từ phút đó
Từng giây trôi yêu thêm
Bao ngày qua bình minh đánh thức xua tan bộn bề nơi anh
Bao ngày qua niềm thương nỗi nhớ bay theo bầu trời trong xanh
Liếc đôi hàng mi mong manh anh thẫn thờ
Muốn hôn nhẹ mái tóc bờ môi em, anh mơ...
Cầm tay anh
Dựa vai anh
Kề bên anh nơi này có anh
Gió mang câu tình ca
Ngàn ánh sao vụt qua nhẹ ôm lấy em
(Yêu em thương em con tim anh chân thành)
Cầm tay anh, dựa vai anh
Kề bên anh nơi này có anh
Khép đôi mi thật lâu
Nguyện mãi bên cạnh nhau
Yêu say đắm như ngày đầu
Mùa xuân đến bình yên cho anh những giấc mơ
Hạ lưu giữ ngày mưa ngọt ngào nên thơ
Mùa thu lá vàng rơi đông sang anh nhớ em
Tình yêu bé nhỏ xin dành tặng riêng em
Còn đó tiếng nói ấy bên tai vấn vương bao ngày qua
Ánh mắt bối rối nhớ thương bao ngày qua
Yêu em anh thẫn thờ, con tim bâng khuâng đâu có ngờ
Chẳng bao giờ phải mong chờ
Đợi ai trong chiều hoàng hôn mờ
Đắm chìm hòa vào vần thơ
Ngắm nhìn khờ dại mộng mơ
Đừng bước vội vàng rồi làm ngơ
Lạnh lùng đó làm bộ dạng thờ ơ
Nhìn anh đi em nha
Hướng nụ cười cho riêng anh nha
Đơn giản là yêu con tim anh lên tiếng thôi
Cầm tay anh, dựa vai anh
Kề bên anh nơi này có anh
Gió mang câu tình ca
Ngàn ánh sao vụt qua nhẹ ôm lấy em
(Yêu em thương em con tim anh chân thành)
Cầm tay anh, dựa vai anh
Kề bên anh nơi này có anh
Khép đôi mi thật lâu
Nguyện mãi bên cạnh nhau
Yêu say đắm như ngày đầu
Mùa xuân đến bình yên cho anh những giấc mơ
Hạ lưu giữ ngày mưa ngọt ngào nên thơ
Mùa thu lá vàng rơi đông sang anh nhớ em
Tình yêu bé nhỏ xin dành tặng riêng em!

Oh-h-h-h nhớ thương em
Oh-h-h-h nhớ thương em lắm
Ah-h-h-h-h phía sau chân trời
Có ai băng qua lối về cùng em đi trên đoạn đường dài
Cầm tay anh, dựa vai anh
Kề bên anh nơi này có anh
Gió mang câu tình ca
Ngàn ánh sao vụt qua nhẹ ôm lấy em
(Yêu em thương em con tim anh chân thành)
Cầm tay anh, dựa vai anh
Kề bên anh nơi này có anh
Khép đôi mi thật lâu
Nguyện mãi bên cạnh nhau
Yêu say đắm như ngày đầu
Mùa xuân đến bình yên cho anh những giấc mơ
Hạ lưu giữ ngày mưa ngọt ngào nên thơ
Mùa thu lá vàng rơi đông sang anh nhớ em
Tình yêu bé nhỏ xin dành tặng riêng em!"""

    pr = cProfile.Profile()
    pr.enable()
    ret = lyric2captions(text)
    pprint(ret)
    pr.disable()
    pr.print_stats(sort='time')