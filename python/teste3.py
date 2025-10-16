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
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)

        with self.root.canvas.before:
            Color(0.9, 0.95, 1, 1)
            bg = RoundedRectangle(size=self.root.size, pos=self.root.pos)
        self.root.bind(size=lambda inst, val: setattr(bg, 'size', val))
        self.root.bind(pos=lambda inst, val: setattr(bg, 'pos', val))

        # Ícone centralizado no topo
        self.icone_area = BoxLayout(size_hint=(1, None), height=dp(160))
        self.root.add_widget(self.icone_area)

        # Campo de entrada
        self.entrada = TextInput(
            hint_text="Digite a palavra para analisar...",
            multiline=False,
            font_size=20,
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.root.add_widget(self.entrada)

        # Botões
        botoes = BoxLayout(size_hint=(1, None), height=dp(50), spacing=10)
        btn_analise = Button(text="Analisar", background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1))
        btn_analise.bind(on_release=self.analisar)
        botoes.add_widget(btn_analise)

        btn_salvar = Button(text="Salvar Tentativa", background_color=(0.1, 0.5, 0.3, 1), color=(1, 1, 1, 1))
        btn_salvar.bind(on_release=self.salvar_tentativa)
        botoes.add_widget(btn_salvar)

        self.root.add_widget(botoes)

        # Área de resultado
        self.resultado_area = BoxLayout(orientation='vertical', spacing=5)
        self.root.add_widget(self.resultado_area)

        self.palavra_original = ""
        self.icone_path = ""
        self.ultima_analise = {}

        self.carregar_palavra()
        return self.root

    def carregar_palavra(self):
        if not os.path.exists(ARQUIVO_PALAVRAS):
            return
        try:
            with open(ARQUIVO_PALAVRAS, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if dados:
                self.palavra_original = dados[0].get("palavra", "").lower()
                self.icone_path = dados[0].get("icone", "")
                self.icone_area.clear_widgets()
                if os.path.exists(self.icone_path):
                    imagem = Image(source=self.icone_path, size_hint=(None, None), size=(dp(130), dp(130)))
                    icone_box = BoxLayout(size_hint=(1, 1), padding=(0, dp(10)))
                    icone_box.add_widget(imagem)
                    self.icone_area.add_widget(icone_box)
        except:
            pass

    def analisar(self, instance):
        palavra_digitada = self.entrada.text.strip().lower()
        self.resultado_area.clear_widgets()
        if not palavra_digitada or not self.palavra_original:
            self.resultado_area.add_widget(Label(text="Digite uma palavra válida.", font_size=18, color=(1, 0, 0, 1)))
            return

        todas_letras = all(l in self.palavra_original for l in palavra_digitada)
        silabas = re.findall(r'\w{2,3}', palavra_digitada)
        silabas_validas = [s for s in silabas if s in self.palavra_original]
        repetidas = [letra for letra in set(palavra_digitada) if palavra_digitada.count(letra) > 1]

        if not todas_letras and not silabas_validas:
            classificacao = "Pré-silábica"
        else:
            classificacao = "Silábica"

        self.ultima_analise = {
            "digitada": palavra_digitada,
            "letras_corretas": todas_letras,
            "silabas": silabas_validas,
            "repetidas": repetidas,
            "classificacao": classificacao
        }

        # Mostra resultados com cor
        cor_letras = (0, 0.5, 0, 1) if todas_letras else (1, 0.2, 0.2, 1)
        cor_silabas = (0.2, 0.4, 0.8, 1) if silabas_validas else (1, 0.4, 0.4, 1)
        cor_rep = (0.6, 0.3, 0.7, 1) if repetidas else (0.5, 0.5, 0.5, 1)
        cor_class = (0, 0.6, 0.3, 1) if classificacao == "Silábica" else (1, 0.2, 0.2, 1)

        self.resultado_area.add_widget(Label(text=f"Letras corretas: {'Sim' if todas_letras else 'Não'}", font_size=18, color=cor_letras))
        self.resultado_area.add_widget(Label(text=f"Sílabas encontradas: {', '.join(silabas_validas) if silabas_validas else 'Nenhuma'}", font_size=18, color=cor_silabas))
        self.resultado_area.add_widget(Label(text=f"Letras repetidas: {', '.join(repetidas) if repetidas else 'Nenhuma'}", font_size=18, color=cor_rep))
        self.resultado_area.add_widget(Label(text=f"Classificação: {classificacao}", font_size=20, bold=True, color=cor_class))

    def salvar_tentativa(self, instance):
        if not self.ultima_analise:
            self.resultado_area.add_widget(Label(text="Nenhuma tentativa para salvar.", font_size=16, color=(1, 0, 0, 1)))
            return
        tentativas = []
        if os.path.exists(ARQUIVO_TENTATIVAS):
            try:
                with open(ARQUIVO_TENTATIVAS, "r", encoding="utf-8") as f:
                    tentativas = json.load(f)
            except:
                pass
        tentativas.append(self.ultima_analise)
        try:
            with open(ARQUIVO_TENTATIVAS, "w", encoding="utf-8") as f:
                json.dump(tentativas, f, ensure_ascii=False, indent=4)
            self.resultado_area.add_widget(Label(text="Tentativa salva com sucesso!", font_size=16, color=(0, 0.5, 0, 1)))
        except Exception as e:
            self.resultado_area.add_widget(Label(text=f"Erro ao salvar: {e}", font_size=16, color=(1, 0, 0, 1)))


if __name__ == '__main__':
    AvaliadorSilabicoApp().run()
