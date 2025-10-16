import json
import os
import csv
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

CURRENT_DIR = os.path.dirname(__file__)
ARQUIVO_AVALIACOES = os.path.join(CURRENT_DIR, "avaliacoes_avancadas.json")
ARQUIVO_CSV = os.path.join(CURRENT_DIR, "relatorio_classificacoes.csv")

HIPOTESES = [
    "Todas",
    "Pré-silábica",
    "Silábica com valor de consoante",
    "Silábica com valor de vogal",
    "Silábica",
    "Silábico-alfabética",
    "Alfabética"
]

class RevisaoItem(BoxLayout):
    def __init__(self, tentativa, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=10, size_hint_y=None, height=dp(220), **kwargs)
        self.tentativa = tentativa

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.add_widget(Label(text=f"Digitada: {tentativa.get('digitada', '')}", font_size=16, color=(0, 0, 0, 1)))
        self.add_widget(Label(text=f"Resgatada: {tentativa.get('resgatada', tentativa.get('palavra_resgatada', '---'))}", font_size=14, color=(0.2, 0.2, 0.2, 1)))
        self.add_widget(Label(text=f"Letras corretas: {'Sim' if tentativa.get('letras_corretas', False) else 'Não'}", font_size=14, color=(0.2, 0.2, 0.2, 1)))
        self.add_widget(Label(text=f"Sílabas válidas: {', '.join(tentativa.get('silabas', tentativa.get('silabas_validas', []))) or 'Nenhuma'}", font_size=14, color=(0.2, 0.2, 0.2, 1)))
        self.add_widget(Label(text=f"Letras repetidas: {', '.join(tentativa.get('repetidas', [])) or 'Nenhuma'}", font_size=14, color=(0.2, 0.2, 0.2, 1)))

        self.spinner = Spinner(
            text=tentativa.get("classificacao", "Indefinida"),
            values=HIPOTESES[1:],
            size_hint=(1, None),
            height=dp(44),
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1)
        )
        self.add_widget(self.spinner)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def get_resultado_editado(self):
        self.tentativa["classificacao"] = self.spinner.text
        return self.tentativa

class RevisorApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)

        with self.root.canvas.before:
            Color(1, 1, 1, 1)
            fundo = RoundedRectangle(size=self.root.size, pos=self.root.pos)
        self.root.bind(size=lambda inst, val: setattr(fundo, 'size', val))
        self.root.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))

        self.itens = []
        self.tentativas = []

        self.spinner_filtro = Spinner(
            text="Todas",
            values=HIPOTESES,
            size_hint=(1, None),
            height=dp(44),
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1)
        )
        self.spinner_filtro.bind(text=self.aplicar_filtro)
        self.root.add_widget(self.spinner_filtro)

        self.scroll = ScrollView()
        self.container = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.root.add_widget(self.scroll)

        botoes = BoxLayout(size_hint=(1, None), height=dp(50), spacing=10)

        salvar_btn = Button(text="Salvar Alterações", background_color=(0.2, 0.6, 0.3, 1), color=(1, 1, 1, 1))
        salvar_btn.bind(on_release=self.salvar_tentativas)
        botoes.add_widget(salvar_btn)

        classificar_btn = Button(text="Classificar Automaticamente", background_color=(1, 0.6, 0.2, 1), color=(0, 0, 0, 1))
        classificar_btn.bind(on_release=self.classificar_todas)
        botoes.add_widget(classificar_btn)

        exportar_btn = Button(text="Exportar CSV", background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1))
        exportar_btn.bind(on_release=self.exportar_csv)
        botoes.add_widget(exportar_btn)

        relatorio_btn = Button(text="Ver Relatório", background_color=(0.5, 0.4, 0.8, 1), color=(1, 1, 1, 1))
        relatorio_btn.bind(on_release=self.mostrar_relatorio)
        botoes.add_widget(relatorio_btn)

        self.root.add_widget(botoes)

        self.carregar_tentativas()
        self.aplicar_filtro(self.spinner_filtro, "Todas")

        return self.root

    def carregar_tentativas(self):
        if os.path.exists(ARQUIVO_AVALIACOES):
            with open(ARQUIVO_AVALIACOES, "r", encoding="utf-8") as f:
                self.tentativas = json.load(f)
        else:
            self.tentativas = []

    def aplicar_filtro(self, spinner, valor):
        self.container.clear_widgets()
        self.itens.clear()
        for tentativa in self.tentativas:
            tipo = tentativa.get("classificacao", "")
            if valor == "Todas" or tipo == valor:
                item = RevisaoItem(tentativa)
                self.container.add_widget(item)
                self.itens.append(item)

    def salvar_tentativas(self, instance):
        dados = [item.get_resultado_editado() for item in self.itens]
        try:
            with open(ARQUIVO_AVALIACOES, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            self.popup_msg("Alterações salvas com sucesso! ✅")
        except Exception as e:
            self.popup_msg(f"Erro ao salvar: {e}")

    def exportar_csv(self, instance):
        try:
            with open(ARQUIVO_CSV, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Digitada", "Resgatada", "Classificacao"])
                for item in self.itens:
                    tentativa = item.get_resultado_editado()
                    writer.writerow([
                        tentativa.get("digitada", ""),
                        tentativa.get("resgatada", tentativa.get("palavra_resgatada", "")),
                        tentativa.get("classificacao", "")
                    ])
            self.popup_msg("Arquivo CSV exportado com sucesso! ✅")
        except Exception as e:
            self.popup_msg(f"Erro ao exportar CSV: {e}")

    def mostrar_relatorio(self, instance):
        contagem = {}
        for tentativa in self.tentativas:
            tipo = tentativa.get("classificacao", "Indefinido")
            contagem[tipo] = contagem.get(tipo, 0) + 1

        texto = "\n".join(f"{tipo}: {quantidade}" for tipo, quantidade in contagem.items())

        layout = BoxLayout(orientation='vertical', padding=20)
        with layout.canvas.before:
            Color(1, 1, 1, 1)
            fundo = RoundedRectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda inst, val: setattr(fundo, 'size', val))
        layout.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))

        layout.add_widget(Label(text=texto, font_size=16, color=(0, 0, 0, 1)))

        popup = Popup(
            title="Relatório de Classificações",
            content=layout,
            size_hint=(0.85, 0.7)
        )
        popup.open()

    def classificar_automaticamente(self, tentativa):
        digitada = tentativa.get('digitada', '').lower()
        resgatada = tentativa.get('resgatada', tentativa.get('palavra_resgatada', '')).lower()
        silabas = tentativa.get('silabas', tentativa.get('silabas_validas', []))
        repetidas = tentativa.get('repetidas', [])
        letras_corretas = tentativa.get('letras_corretas', False)

        vogais = 'aeiou'
        consoantes = ''.join(set(resgatada) - set(vogais))
        digitadas_consoantes = [l for l in digitada if l in consoantes]
        digitadas_vogais = [l for l in digitada if l in vogais and l in resgatada]

        if not letras_corretas and not silabas:
            return "Pré-silábica"
        elif len(digitadas_consoantes) <= 2 and digitadas_consoantes:
            return "Silábica com valor de consoante"
        elif len(digitadas_vogais) <= 2 and digitadas_vogais:
            return "Silábica com valor de vogal"
        elif silabas and letras_corretas:
            return "Silábico-alfabética"
        elif letras_corretas and not repetidas:
            return "Alfabética"
        else:
            return "Silábica"

    def classificar_todas(self, instance):
        for tentativa in self.tentativas:
            tentativa["classificacao"] = self.classificar_automaticamente(tentativa)
        self.aplicar_filtro(self.spinner_filtro, self.spinner_filtro.text)
        self.popup_msg("Classificação automática aplicada às tentativas!")

    def popup_msg(self, msg):
        popup = Popup(
            title="Revisor de Classificações",
            content=Label(text=msg, font_size=16, color=(0, 0, 0, 1)),
            size_hint=(0.7, 0.3)
        )
        popup.open()

if __name__ == '__main__':
    RevisorApp().run()
