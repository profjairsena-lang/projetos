import os
import json
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

# Caminhos dos arquivos
CURRENT_DIR = os.path.dirname(__file__)
ARQUIVO_PALAVRAS = os.path.join(CURRENT_DIR, "palavras.json")
ARQUIVO_TENTATIVAS = os.path.join(CURRENT_DIR, "tentativas.json")
ARQUIVO_ANALISES = os.path.join(CURRENT_DIR, "avaliacoes_avancadas.json")


class AvaliadorSilabicoApp(App):
    def build(self):
        self.index = 0
        self.tentativas = []

        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)
        with self.root.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            fundo = RoundedRectangle(size=self.root.size, pos=self.root.pos)
        self.root.bind(size=lambda inst, val: setattr(fundo, 'size', val))
        self.root.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))

        self.icone_area = BoxLayout(size_hint=(1, None), height=dp(160))
        self.root.add_widget(self.icone_area)

        self.input_palavra = TextInput(
            hint_text="Digite uma palavra para analisar...",
            multiline=False,
            font_size=20,
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.root.add_widget(self.input_palavra)

        botoes = BoxLayout(size_hint=(1, None), height=dp(50), spacing=10)
        btn_analisar = Button(text="Analisar", font_size=18, background_normal='',
                              background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1))
        btn_analisar.bind(on_release=self.analisar)
        botoes.add_widget(btn_analisar)

        btn_proximo = Button(text="Próximo", font_size=18, background_normal='',
                             background_color=(0.5, 0.5, 0.5, 1), color=(1, 1, 1, 1))
        btn_proximo.bind(on_release=self.proximo)
        botoes.add_widget(btn_proximo)

        self.root.add_widget(botoes)
        self.resultado_area = BoxLayout(orientation='vertical', spacing=5)
        self.root.add_widget(self.resultado_area)

        self.carregar_palavras()
        self.exibir_icone_atual()
        return self.root

    def carregar_palavras(self):
        self.lista_palavras = []
        if os.path.exists(ARQUIVO_PALAVRAS):
            with open(ARQUIVO_PALAVRAS, "r", encoding="utf-8") as f:
                try:
                    self.lista_palavras = json.load(f)
                except:
                    pass

    def exibir_icone_atual(self):
        self.icone_area.clear_widgets()
        self.resultado_area.clear_widgets()
        self.input_palavra.text = ""

        if self.index >= len(self.lista_palavras):
            self.exibir_historico_popup()
            return

        entrada = self.lista_palavras[self.index]
        self.palavra_original = entrada.get("palavra", "").lower()
        caminho_icone = entrada.get("icone", "")

        if os.path.exists(caminho_icone):
            container = BoxLayout()
            container.add_widget(Label())
            img = Image(source=caminho_icone, size_hint=(None, None), size=(dp(130), dp(130)))
            centro = BoxLayout(size_hint=(None, 1), width=dp(130))
            centro.add_widget(img)
            container.add_widget(centro)
            container.add_widget(Label())
            self.icone_area.add_widget(container)

    def verificar_silabica_avancada(self, resgatada, digitada):
        resgatada = resgatada.lower()
        digitada = digitada.lower()

        letras_validas = [l for l in digitada if l in resgatada]
        repetidas = [l for l in set(digitada) if digitada.count(l) > 1]
        silabas = re.findall(r'\w{2,3}', digitada)
        silabas_validas = [s for s in silabas if s in resgatada]

        vogais = "aeiou"
        consoantes_resgatada = [l for l in resgatada if l not in vogais]
        vogais_resgatada = [l for l in resgatada if l in vogais]

        digitadas_consoantes = [l for l in digitada if l in consoantes_resgatada]
        digitadas_vogais = [l for l in digitada if l in vogais_resgatada]

        if len(digitadas_consoantes) <= 2 and silabas_validas:
            tipo = "Silábica com valor de consoante"
        elif len(digitadas_vogais) <= 2 and silabas_validas:
            tipo = "Silábica com valor de vogal"
        elif not letras_validas and not silabas_validas:
            tipo = "Pré-silábica"
        else:
            tipo = "Silábica"

        return {
            "letras_validas": letras_validas,
            "silabas_validas": silabas_validas,
            "repetidas": repetidas,
            "classificacao": tipo
        }

    def analisar(self, instance):
        digitada = self.input_palavra.text.strip().lower()
        self.resultado_area.clear_widgets()

        if not digitada or not hasattr(self, 'palavra_original'):
            self.resultado_area.add_widget(Label(text="Digite uma palavra válida.", font_size=18, color=(1, 0, 0, 1)))
            return

        analise = self.verificar_silabica_avancada(self.palavra_original, digitada)
        tipo = analise["classificacao"]

        tentativa = {
            "palavra_resgatada": self.palavra_original,
            "digitada": digitada,
            "letras_validas": analise["letras_validas"],
            "silabas_validas": analise["silabas_validas"],
            "repetidas": analise["repetidas"],
            "classificacao": tipo
        }

        self.tentativas.append(tentativa)

        try:
            historico = []
            if os.path.exists(ARQUIVO_ANALISES):
                with open(ARQUIVO_ANALISES, "r", encoding="utf-8") as f:
                    historico = json.load(f)
            historico.append(tentativa)
            with open(ARQUIVO_ANALISES, "w", encoding="utf-8") as f:
                json.dump(historico, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.resultado_area.add_widget(Label(text=f"Erro ao salvar análise: {e}", font_size=14, color=(1, 0, 0, 1)))
            return

        cor = lambda cond: (0, 0.6, 0.3, 1) if cond else (1, 0.2, 0.2, 1)

        self.resultado_area.add_widget(Label(text=f"Letras válidas: {', '.join(analise['letras_validas']) or 'Nenhuma'}", font_size=18, color=cor(analise["letras_validas"])))
        self.resultado_area.add_widget(Label(text=f"Sílabas válidas: {', '.join(analise['silabas_validas']) or 'Nenhuma'}", font_size=18, color=cor(analise["silabas_validas"])))
        self.resultado_area.add_widget(Label(text=f"Letras repetidas: {', '.join(analise['repetidas']) or 'Nenhuma'}", font_size=18, color=(0.5, 0.3, 0.7, 1)))
        self.resultado_area.add_widget(Label(
            text=f"Classificação: {analise['classificacao']}",
            font_size=20,
            color=cor(analise["classificacao"] != "Pré-silábica")
        ))

    def proximo(self, instance):
        self.index += 1
        self.exibir_icone_atual()

    def exibir_historico_popup(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        with layout.canvas.before:
            Color(1, 1, 1, 1)  # fundo branco
            fundo = RoundedRectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda inst, val: setattr(fundo, 'size', val))
        layout.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))

        layout.add_widget(Label(text="Histórico de Tentativas", font_size=24, color=(0, 0, 0, 1)))

        for tentativa in self.tentativas:
            bloco = BoxLayout(orientation='vertical', spacing=5)
            bloco.add_widget(Label(text=f"Palavra original: {tentativa['palavra_resgatada']}", font_size=16, color=(0, 0, 0, 1)))
            bloco.add_widget(Label(text=f"Digitada: {tentativa['digitada']}", font_size=16, color=(0.1, 0.1, 0.6, 1)))
            bloco.add_widget(Label(text=f"Letras válidas: {', '.join(tentativa['letras_validas']) or 'Nenhuma'}", font_size=16, color=(0, 0, 0, 1)))
            bloco.add_widget(Label(text=f"Sílabas válidas: {', '.join(tentativa['silabas_validas']) or 'Nenhuma'}", font_size=16, color=(0, 0, 0, 1)))
            bloco.add_widget(Label(text=f"Letras repetidas: {', '.join(tentativa['repetidas']) or 'Nenhuma'}", font_size=16, color=(0, 0, 0, 1)))
            bloco.add_widget(Label(text=f"Classificação: {tentativa['classificacao']}", font_size=16, color=(0.2, 0.4, 0.2, 1)))
            layout.add_widget(bloco)

        popup = Popup(title="Histórico de Tentativas", content=layout, size_hint=(0.85, 0.85))
        popup.open()


if __name__ == '__main__':
    AvaliadorSilabicoApp().run()
