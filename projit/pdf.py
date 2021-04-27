from fpdf import FPDF

class PDF(FPDF):

    def setup(self):
        self.add_page()

    def add_title(self, title):
        self.set_xy(0.0,0.0)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(50, 50, 50)
        self.cell(w=210.0, h=40.0, align='C', txt=title, border=0)

    def add_description(self, description):
        self.set_xy(10.0,40.0)
        self.set_text_color(32.0, 32.0, 32.0)
        self.set_font('Arial', '', 12)
        self.multi_cell(0,10,description)


