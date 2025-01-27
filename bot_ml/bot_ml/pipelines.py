import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from datetime import datetime

currency_style = NamedStyle(name="currency_BRL")
currency_style.number_format = 'R$ #,##0.00'


class BotMlPipeline:
    def __init__(self):
        self.results = []
        self.date_file = datetime.now().strftime("%d/%m/%Y")

    def process_item(self, item, spider):
        self.results.append(item)
        return item

    def close_spider(self, spider):
        df = pd.DataFrame(self.results)

        output_file = f"resultados-{self.date_file}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = f"Resultados-{self.date_file}"

        header_font = Font(bold=True, size=12)
        headers = [col.upper() for col in df.columns.tolist()] 
        ws.append(headers)
        for col_num, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        for _, row in df.iterrows():
            current_row = ws.max_row + 1
            for col_num, (col_name, value) in enumerate(row.items(), start=1):
                cell = ws.cell(row=current_row, column=col_num)

                if col_name == 'link' and pd.notna(value):
                    cell.hyperlink = value
                    cell.font = Font(color="0000FF", underline="single")
                elif col_name == 'valor' and pd.notna(value):
                    cell.value = float(value)
                    cell.style = currency_style
                else:
                    cell.value = value

        # Ajusta a largura das colunas automaticamente
        # for col in ws.columns:
        #     max_length = max(len(str(cell.value) if cell.value else "") for cell in col)
        #     ws.column_dimensions[col[0].column_letter].width = max_length + 2

        wb.save(output_file)
        print(f"Arquivo Excel salvo em: {output_file}")
