from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER, inch
from reportlab.graphics.shapes import Line, LineShape, Drawing
from reportlab.lib.colors import Color
from datetime import date


### variáveis para serem definidas no report ###
diretoria = "ABC4"
data_hoje = "13 jan 2023"

def rgba(r,g,b,a):
    return r/256, g/256, b/256, a

class FooterCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.width, self.height = LETTER

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if (self._pageNumber > 1):
                self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        page = f"Página {page_count} de {self._pageNumber}"
        today = date.today()
        x = 128
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        
        self.drawImage("static/lr.png", self.width-inch*8-5, 
                       self.height-50, width=100, height=20, 
                       preserveAspectRatio=True)
        
        self.drawString(273, 745, 'Uso interno.')

        
        self.drawImage("static/ohka.png", self.width - inch * 2, 
                       self.height-50, width=100, height=30, 
                       preserveAspectRatio=True, mask='auto')
        
        self.line(30, 740, LETTER[0] - 50, 740)
        self.line(66, 78, LETTER[0] - 66, 78)
        self.setFont('Times-Roman', 10)
        self.drawString(LETTER[0]-x, 65, page)
        self.drawString(65, 65, today.strftime("%d/%m/%Y"))
        self.drawString(273, 65, 'Uso interno.')
        self.restoreState()

class PDFPSReporte:

    def __init__(self, path):
        self.path = path
        self.styleSheet = getSampleStyleSheet()
        self.elements = []

        r,g,b,a = rgba(245,121,33,1)
        self.color_iu_orange_0 = Color(r,g,b,a)  
        
        r,g,b,a = rgba(246,137,32,1)    
        self.color_iu_orange_1 = Color(r,g,b,a)
        
        r,g,b,a = rgba(250,157,28,1)
        self.color_iu_orange_2 = Color(r,g,b,a)
        
        r,g,b,a = rgba(246,137,32,1)
        self.color_iu_orange_linhas = Color(r,g,b,a)
        
        r,g,b,a = rgba(13,60,114,1)
        self.color_iu_blue_0 = Color(r,g,b,a) 
            
        r,g,b,a = rgba(0,75,142,1)
        self.color_iu_blue_1 = Color(r,g,b,a) 


        self.firstPage()
        self.nextPagesHeader(True)
        self.remoteSessionTableMaker()
        self.nextPagesHeader(False)
        self.inSiteSessionTableMaker()
        self.nextPagesHeader(False)
        self.extraActivitiesTableMaker()
        self.nextPagesHeader(False)
        self.summaryTableMaker()
        # Build
        self.doc = SimpleDocTemplate(path, pagesize=LETTER)
        self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

    def firstPage(self):
        img = Image('static/lr.png', kind='proportional')
        img.drawHeight = 0.5*inch
        img.drawWidth = 2.4*inch
        img.hAlign = 'LEFT'
        self.elements.append(img)

        spacer = Spacer(30, 100)
        self.elements.append(spacer)

        img = Image('static/ohka.png')
        img.drawHeight = 2.5*inch
        img.drawWidth = 5.5*inch
        self.elements.append(img)

        spacer = Spacer(10, 250)
        self.elements.append(spacer)

        psDetalle = ParagraphStyle('Resumen', fontSize=9, leading=14, justifyBreaks=1, alignment=TA_LEFT, justifyLastLine=1)
        text = f"""
        REPORTE DE SERVICIOS PROFESIONALES<br/>
        Diretoria: {diretoria}<br/>
        Data: {data_hoje}<br/>
        <!--Fecha de actualización: 01-Abril-2020<br/>-->
        """
        paragraphReportSummary = Paragraph(text, psDetalle)
        self.elements.append(paragraphReportSummary)
        self.elements.append(PageBreak())

    def nextPagesHeader(self, isSecondPage):
        if isSecondPage:
            psHeaderText = ParagraphStyle('Hed0', fontSize=16, alignment=TA_LEFT, 
                                          borderWidth=3, textColor=self.color_iu_orange_0)
            text = 'REPORTE DE SESIONES'
            paragraphReportHeader = Paragraph(text, psHeaderText)
            self.elements.append(paragraphReportHeader)

            spacer = Spacer(10, 10)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-15, 0, 483, 0)
            line.strokeColor = self.color_iu_orange_linhas
            line.strokeWidth = 2
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 1)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-15, 0, 483, 0)
            line.strokeColor = self.color_iu_orange_linhas
            line.strokeWidth = 0.5
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 22)
            self.elements.append(spacer)

    def remoteSessionTableMaker(self):        
        psHeaderText = ParagraphStyle('Hed0', fontSize=12, alignment=TA_LEFT, borderWidth=3, textColor=self.color_iu_blue_0)
        text = 'SESIONES REMOTAS'
        paragraphReportHeader = Paragraph(text, psHeaderText)
        self.elements.append(paragraphReportHeader)

        spacer = Spacer(10, 22)
        self.elements.append(spacer)
        """
        Create the line items
        """
        d = []
        textData = ["No.", "Fecha", "Hora Inicio", "Hora Fin", "Tiempo Total"]
                
        fontSize = 8
        centered = ParagraphStyle(name="centered", alignment=TA_CENTER)
        for text in textData:
            ptext = "<font size='%s'><b>%s</b></font>" % (fontSize, text)
            titlesTable = Paragraph(ptext, centered)
            d.append(titlesTable)        

        data = [d]
        lineNum = 1
        formattedLineData = []

        alignStyle = [ParagraphStyle(name="01", alignment=TA_CENTER),
                      ParagraphStyle(name="02", alignment=TA_LEFT),
                      ParagraphStyle(name="03", alignment=TA_CENTER),
                      ParagraphStyle(name="04", alignment=TA_CENTER),
                      ParagraphStyle(name="05", alignment=TA_CENTER)]

        for row in range(10):
            lineData = [str(lineNum), "Miércoles, 11 de diciembre de 2019", 
                                            "17:30", "19:24", "1:54"]
            #data.append(lineData)
            columnNumber = 0
            for item in lineData:
                ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
                p = Paragraph(ptext, alignStyle[columnNumber])
                formattedLineData.append(p)
                columnNumber = columnNumber + 1
            data.append(formattedLineData)
            formattedLineData = []
            
        # Row for total
        totalRow = ["Total de Horas", "", "", "", "30:15"]
        for item in totalRow:
            ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
            p = Paragraph(ptext, alignStyle[1])
            formattedLineData.append(p)
        data.append(formattedLineData)
        
        #print(data)
        table = Table(data, colWidths=[50, 200, 80, 80, 80])
        tStyle = TableStyle([ #('GRID',(0, 0), (-1, -1), 0.5, grey),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                #('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ("ALIGN", (1, 0), (1, -1), 'RIGHT'),
                ('LINEABOVE', (0, 0), (-1, -1), 1, self.color_iu_blue_1),
                ('BACKGROUND',(0, 0), (-1, 0), self.color_iu_orange_linhas),
                ('BACKGROUND',(0, -1),(-1, -1), self.color_iu_blue_1),
                ('SPAN',(0,-1),(-2,-1))
                ])
        table.setStyle(tStyle)
        self.elements.append(table)

    def inSiteSessionTableMaker(self):
        self.elements.append(PageBreak())
        psHeaderText = ParagraphStyle('Hed0', fontSize=12, alignment=TA_LEFT, borderWidth=3, textColor=self.color_iu_blue_0)
        text = 'SESIONES EN SITIO'
        paragraphReportHeader = Paragraph(text, psHeaderText)
        self.elements.append(paragraphReportHeader)

        spacer = Spacer(10, 22)
        self.elements.append(spacer)
        """
        Create the line items
        """
        d = []
        textData = ["No.", "Fecha", "Hora Inicio", "Hora Fin", "Tiempo Total"]
                
        fontSize = 8
        centered = ParagraphStyle(name="centered", alignment=TA_CENTER)
        for text in textData:
            ptext = "<font size='%s'><b>%s</b></font>" % (fontSize, text)
            titlesTable = Paragraph(ptext, centered)
            d.append(titlesTable)        

        data = [d]
        lineNum = 1
        formattedLineData = []

        alignStyle = [ParagraphStyle(name="01", alignment=TA_CENTER),
                      ParagraphStyle(name="02", alignment=TA_LEFT),
                      ParagraphStyle(name="03", alignment=TA_CENTER),
                      ParagraphStyle(name="04", alignment=TA_CENTER),
                      ParagraphStyle(name="05", alignment=TA_CENTER)]

        for row in range(10):
            lineData = [str(lineNum), "Miércoles, 11 de diciembre de 2019", 
                                            "17:30", "19:24", "1:54"]
            #data.append(lineData)
            columnNumber = 0
            for item in lineData:
                ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
                p = Paragraph(ptext, alignStyle[columnNumber])
                formattedLineData.append(p)
                columnNumber = columnNumber + 1
            data.append(formattedLineData)
            formattedLineData = []
            
        # Row for total
        totalRow = ["Total de Horas", "", "", "", "30:15"]
        for item in totalRow:
            ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
            p = Paragraph(ptext, alignStyle[1])
            formattedLineData.append(p)
        data.append(formattedLineData)
        
        #print(data)
        table = Table(data, colWidths=[50, 200, 80, 80, 80])
        tStyle = TableStyle([ #('GRID',(0, 0), (-1, -1), 0.5, grey),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                #('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ("ALIGN", (1, 0), (1, -1), 'RIGHT'),
                ('LINEABOVE', (0, 0), (-1, -1), 1, self.color_iu_blue_1),
                ('BACKGROUND',(0, 0), (-1, 0), self.color_iu_orange_linhas),
                ('BACKGROUND',(0, -1),(-1, -1), self.color_iu_blue_1),
                ('SPAN',(0,-1),(-2,-1))
                ])
        table.setStyle(tStyle)
        self.elements.append(table)

    def extraActivitiesTableMaker(self):
        self.elements.append(PageBreak())
        psHeaderText = ParagraphStyle('Hed0', fontSize=12, alignment=TA_LEFT, borderWidth=3, textColor=self.color_iu_blue_0)
        text = 'OTRAS ACTIVIDADES Y DOCUMENTACIÓN'
        paragraphReportHeader = Paragraph(text, psHeaderText)
        self.elements.append(paragraphReportHeader)

        spacer = Spacer(10, 22)
        self.elements.append(spacer)
        """
        Create the line items
        """
        d = []
        textData = ["No.", "Fecha", "Hora Inicio", "Hora Fin", "Tiempo Total"]
                
        fontSize = 8
        centered = ParagraphStyle(name="centered", alignment=TA_CENTER)
        for text in textData:
            ptext = "<font size='%s'><b>%s</b></font>" % (fontSize, text)
            titlesTable = Paragraph(ptext, centered)
            d.append(titlesTable)        

        data = [d]
        lineNum = 1
        formattedLineData = []

        alignStyle = [ParagraphStyle(name="01", alignment=TA_CENTER),
                      ParagraphStyle(name="02", alignment=TA_LEFT),
                      ParagraphStyle(name="03", alignment=TA_CENTER),
                      ParagraphStyle(name="04", alignment=TA_CENTER),
                      ParagraphStyle(name="05", alignment=TA_CENTER)]

        for row in range(10):
            lineData = [str(lineNum), "Miércoles, 11 de diciembre de 2019", 
                                            "17:30", "19:24", "1:54"]
            #data.append(lineData)
            columnNumber = 0
            for item in lineData:
                ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
                p = Paragraph(ptext, alignStyle[columnNumber])
                formattedLineData.append(p)
                columnNumber = columnNumber + 1
            data.append(formattedLineData)
            formattedLineData = []
            
        # Row for total
        totalRow = ["Total de Horas", "", "", "", "30:15"]
        for item in totalRow:
            ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
            p = Paragraph(ptext, alignStyle[1])
            formattedLineData.append(p)
        data.append(formattedLineData)
        
        #print(data)
        table = Table(data, colWidths=[50, 200, 80, 80, 80])
        tStyle = TableStyle([ #('GRID',(0, 0), (-1, -1), 0.5, grey),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                #('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ("ALIGN", (1, 0), (1, -1), 'RIGHT'),
                ('LINEABOVE', (0, 0), (-1, -1), 1, self.color_iu_blue_1),
                ('BACKGROUND',(0, 0), (-1, 0), self.color_iu_orange_linhas),
                ('BACKGROUND',(0, -1),(-1, -1), self.color_iu_blue_1),
                ('SPAN',(0,-1),(-2,-1))
                ])
        table.setStyle(tStyle)
        self.elements.append(table)

    def summaryTableMaker(self):
        self.elements.append(PageBreak())
        psHeaderText = ParagraphStyle('Hed0', fontSize=12, alignment=TA_LEFT, borderWidth=3, textColor=self.color_iu_blue_0)
        text = 'REGISTRO TOTAL DE HORAS'
        paragraphReportHeader = Paragraph(text, psHeaderText)
        self.elements.append(paragraphReportHeader)

        spacer = Spacer(10, 22)
        self.elements.append(spacer)
        """
        Create the line items
        """

        tStyle = TableStyle([
                   ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                   #('VALIGN', (0, 0), (-1, -1), 'TOP'),
                   ("ALIGN", (1, 0), (1, -1), 'RIGHT'),
                   ('LINEABOVE', (0, 0), (-1, -1), 1, self.color_iu_blue_1),
                   ('BACKGROUND',(-2, -1),(-1, -1), self.color_iu_orange_2)
                   ])

        fontSize = 8
        lineData = [["Sesiones remotas", "30:15"],
                    ["Sesiones en sitio", "00:00"],
                    ["Otras actividades", "00:00"],
                    ["Total de horas consumidas", "30:15"]]

        # for row in lineData:
        #     for item in row:
        #         ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
        #         p = Paragraph(ptext, centered)
        #         formattedLineData.append(p)
        #     data.append(formattedLineData)
        #     formattedLineData = []

        table = Table(lineData, colWidths=[400, 100])
        table.setStyle(tStyle)
        self.elements.append(table)

        # Total de horas contradas vs horas consumidas
        data = []
        formattedLineData = []

        lineData = [["Total de horas contratadas", "120:00"],
                    ["Horas restantes por consumir", "00:00"]]

        # for row in lineData:
        #     for item in row:
        #         ptext = "<b>{}</b>".format(item)
        #         p = Paragraph(ptext, self.styleSheet["BodyText"])
        #         formattedLineData.append(p)
        #     data.append(formattedLineData)
        #     formattedLineData = []

        table = Table(lineData, colWidths=[400, 100])
        tStyle = TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ("ALIGN", (1, 0), (1, -1), 'RIGHT'),
                ('BACKGROUND', (0, 0), (1, 0), self.color_iu_blue_1),
                ('BACKGROUND', (0, 1), (1, 1), self.color_iu_orange_1),
                ])
        table.setStyle(tStyle)

        spacer = Spacer(10, 50)
        self.elements.append(spacer)
        self.elements.append(table)


if __name__ == '__main__':
    report = PDFPSReporte('psreport.pdf')