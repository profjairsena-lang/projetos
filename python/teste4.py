import os
import json
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

CURRENT_DIR = os.path.dirname(__file__)
ARQUIVO_PALAVRAS = os.path.join(CURRENT_DIR, "palavras.json")
ARQUIVO_TENTATIVAS = os.path.join(CURRENT_DIR, "tentativas.json")


class AvaliadorSilabicoApp(App):
    def build(self):
        self.index = 0
        self.tentativas = []

        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)

        with self.root.canvas.before:
            Color(0.9, 0.95, 1, 1)
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

        btn_analisar = Button(
            text="Analisar",
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(50),
            font_size=20
        )
        btn_analisar.bind(on_release=self.analisar)
        self.root.add_widget(btn_analisar)

        self.resultado_area = BoxLayout(orientation='vertical', spacing=8)
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
        if self.index >= len(self.lista_palavras):
            self.exibir_historico_final()
            return

        entrada = self.lista_palavras[self.index]
        self.palavra_original = entrada.get("palavra", "").lower()
        caminho_icone = entrada.get("icone", "")
        if os.path.exists(caminho_icone):
            img = Image(source=caminho_icone, size_hint=(None, None), size=(dp(130), dp(130)))
            centro = BoxLayout()
            centro.add_widget(img)
            self.icone_area.add_widget(centro)

    def analisar(self, instance):
        digitada = self.input_palavra.text.strip().lower()
        self.resultado_area.clear_widgets()

        if not digitada or not hasattr(self, 'palavra_original'):
            self.resultado_area.add_widget(Label(text="Digite uma palavra válida.", font_size=18, color=(1, 0, 0, 1)))
            return

        todas_letras = all(l in self.palavra_original for l in digitada)
        silabas = re.findall(r'\w{2,3}', digitada)
        silabas_validas = [s for s in silabas if s in self.palavra_original]
        repetidas = [letra for letra in set(digitada) if digitada.count(letra) > 1]

        vogais = "aeiou"
        consoantes = ''.join(set(self.palavra_original) - set(vogais))
        digitadas_consoantes = [l for l in digitada if l in consoantes]
        digitadas_vogais = [l for l in digitada if l in vogais and l in self.palavra_original]

        if len(digitadas_consoantes) <= 2 and digitadas_consoantes:
            classificacao = "Silábica com valor de consoante"
        elif len(digitadas_vogais) <= 2 and digitadas_vogais:
            classificacao = "Silábica com valor de vogal"
        elif not todas_letras and not silabas_validas:
            classificacao = "Pré-silábica"
        else:
            classificacao = "Silábica"

        cor1 = (0, 0.5, 0, 1) if todas_letras else (1, 0.2, 0.2, 1)
        cor2 = (0.2, 0.4, 0.8, 1) if silabas_validas else (1, 0.4, 0.4, 1)
        cor3 = (0.6, 0.3, 0.7, 1) if repetidas else (0.5, 0.5, 0.5, 1)
        cor4 = (0, 0.6, 0.3, 1) if "Silábica" in classificacao else (1, 0.3, 0.3, 1)

        self.resultado_area.add_widget(Label(text=f"Letras corretas: {'Sim' if todas_letras else 'Não'}", font_size=18, color=cor1))
        self.resultado_area.add_widget(Label(text=f"Sílabas válidas: {', '.join(silabas_validas) if silabas_validas else 'Nenhuma'}", font_size=18, color=cor2))
        self.resultado_area.add_widget(Label(text=f"Letras repetidas: {', '.join(repetidas) if repetidas else 'Nenhuma'}", font_size=18, color=cor3))
        self.resultado_area.add_widget(Label(text=f"Classificação: {classificacao}", font_size=20, bold=True, color=cor4))

        self.tentativas.append({
            "palavra_original": self.palavra_original,
            "digitada": digitada,
            "letras_corretas": todas_letras,
            "silabas": silabas_validas,
            "repetidas": repetidas,
            "classificacao": classificacao
        })

        self.index += 1
        self.input_palavra.text = ""
        self.exibir_icone_atual()

    def exibir_historico_final(self):
        self.icone_area.clear_widgets()
        self.resultado_area.clear_widgets()
        self.input_palavra.disabled = True

        titulo = Label(text="Histórico de Tentativas", font_size=24, color=(0, 0.4, 0.6, 1))
        self.resultado_area.add_widget(titulo)

        for tentativa in self.tentativas:
            item = BoxLayout(orientation='vertical', padding=10, spacing=5)
            item.add_widget(Label(text=f"Palavra original: {tentativa['palavra_original']}", font_size=16, color=(0.3, 0.3, 0.3, 1)))
            item.add_widget(Label(text=f"Digitada: {tentativa['digitada']}", font_size=16, color=(0.1, 0.2, 0.7, 1)))
            item.add_widget(Label(
                text=f"Classificação: {tentativa['classificacao']}",
                font_size=16,
                color=(0, 0.6, 0.3, 1) if "Silábica" in tentativa["classificacao"] else (1, 0.2, 0.2, 1)
            ))
            self.resultado_area.add_widget(item)

        try:
            with open(ARQUIVO_TENTATIVAS, "w", encoding="utf-8") as f:
                json.dump(self.tentativas, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.resultado_area.add_widget(Label(text=f"Erro ao salvar histórico: {e}", font_size=14, color=(1, 0, 0, 1)))


if __name__ == '__main__':
    AvaliadorSilabicoApp().run()
