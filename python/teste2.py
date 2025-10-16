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


class AvaliadorSilabicoApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Fundo da janela
        with self.root.canvas.before:
            Color(0.9, 0.95, 1, 1)
            bg = RoundedRectangle(size=self.root.size, pos=self.root.pos)
        self.root.bind(size=lambda inst, val: setattr(bg, 'size', val))
        self.root.bind(pos=lambda inst, val: setattr(bg, 'pos', val))

        # Área de exibição da palavra e ícone
        self.exibir_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, None), height=dp(200))
        self.root.add_widget(self.exibir_layout)

        # Campo de entrada
        self.entrada_texto = TextInput(
            hint_text="Digite a palavra para avaliar...",
            multiline=False,
            font_size=20,
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(50)
        )
        self.root.add_widget(self.entrada_texto)

        # Botões
        botoes_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=10)
        btn_mostrar = Button(text="Mostrar Palavra e Ícone", background_color=(0.1, 0.5, 0.8, 1), color=(1, 1, 1, 1))
        btn_mostrar.bind(on_release=self.mostrar_dados)
        botoes_layout.add_widget(btn_mostrar)

        btn_analise = Button(text="Analisar", background_color=(0.2, 0.7, 0.3, 1), color=(1, 1, 1, 1))
        btn_analise.bind(on_release=self.analisar_palavra)
        botoes_layout.add_widget(btn_analise)

        self.root.add_widget(botoes_layout)

        # Resultado da análise
        self.resultado = Label(text="", font_size=20, color=(0, 0, 0, 1))
        self.root.add_widget(self.resultado)

        # Carrega dados
        self.palavra_original = ""
        self.icone_path = ""
        return self.root

    def mostrar_dados(self, instance):
        self.exibir_layout.clear_widgets()
        if not os.path.exists(ARQUIVO_PALAVRAS):
            self.resultado.text = "Arquivo não encontrado."
            return

        try:
            with open(ARQUIVO_PALAVRAS, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if not dados:
                self.resultado.text = "Nenhuma palavra salva ainda."
                return

            entrada = dados[0]
            self.palavra_original = entrada.get("palavra", "").lower()
            self.icone_path = entrada.get("icone", "")

            if os.path.exists(self.icone_path):
                img = Image(source=self.icone_path, size_hint=(None, None), size=(dp(130), dp(130)))
                icone_box = BoxLayout(size_hint=(1, None), height=dp(140))
                icone_box.add_widget(img)
                self.exibir_layout.add_widget(icone_box)

            palavra_label = Label(text=self.palavra_original, font_size=32, color=(0, 0, 0, 1), size_hint_y=None, height=dp(40))
            palavra_box = BoxLayout(size_hint=(1, None), height=dp(50))
            palavra_box.add_widget(palavra_label)
            self.exibir_layout.add_widget(palavra_box)

        except Exception as e:
            self.resultado.text = f"Erro ao abrir arquivo: {e}"

    def analisar_palavra(self, instance):
        digitada = self.entrada_texto.text.strip().lower()
        if not digitada or not self.palavra_original:
            self.resultado.text = "Digite uma palavra e carregue a original primeiro."
            return

        analisada = []

        # 1. Todas as letras estão na palavra original?
        todas_contem = all(letra in self.palavra_original for letra in digitada)

        # 2. Verifica sílabas (simples: assume sílaba como par de letras que aparece na palavra original)
        silabas_digitadas = re.findall(r'\w{2,3}', digitada)
        silabas_validas = [s for s in silabas_digitadas if s in self.palavra_original]

        # 3. Verifica repetição
        repetidas = [letra for letra in set(digitada) if digitada.count(letra) > 1]

        # 4. Verifica se não atende a nenhuma regra
        if not todas_contem and not silabas_validas:
            classificacao = "Pré-silábica"
        else:
            classificacao = "Silábica"

        # Construção da análise
        texto = f"[Análise de '{digitada}']\n"
        texto += f"Todas letras existem na original? {'Sim' if todas_contem else 'Não'}\n"
        texto += f"Silabas encontradas: {', '.join(silabas_validas) if silabas_validas else 'Nenhuma'}\n"
        texto += f"Letras repetidas: {', '.join(repetidas) if repetidas else 'Nenhuma'}\n"
        texto += f"Classificação final: {classificacao}"

        self.resultado.text = texto


if __name__ == '__main__':
    AvaliadorSilabicoApp().run()
