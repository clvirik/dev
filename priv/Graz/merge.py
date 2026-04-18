from pypdf import PdfWriter

merger = PdfWriter()

merger.append("CV_english.pdf")
merger.append("Graz_CL.pdf")
merger.append("Research_statement.pdf")
merger.append("Diploma Supplement - digitalt signert (Bachelor i fysikk og astronomi).pdf")
merger.append("Diploma Supplement - digitalt signert (Master i fysikk).pdf")
merger.append("Masterthesis.pdf")
merger.write("merged.pdf")
merger.close()