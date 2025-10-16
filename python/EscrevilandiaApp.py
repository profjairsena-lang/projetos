import os
import json
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_EMOJIS = os.path.join(CURRENT_DIR, "emojis")
ARQUIVO_PALAVRAS = os.path.join(CURRENT_DIR, "palavras.json")


class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.85, 0.92, 1, 1)
        self.color = (0, 0, 0, 1)
        with self.canvas.before:
            self.rect_color = Color(0.85, 0.92, 1, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class PalavraEmoji(BoxLayout):
    def __init__(self, numero, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 10
        self.size_hint_y = None
        self.height = 60
        self.padding = [10, 5]
        self.icone_path = None

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(pos=self._update_rect, size=self._update_rect)

        self.icon_display_image = Image(source="", size_hint_x=0.2)
        self.word_input = TextInput(hint_text="Digite uma palavra...", multiline=False, font_size=18, size_hint_x=0.5)
        self.icon_button = CustomButton(text="Escolher Ícone", size_hint_x=0.3)
        self.icon_button.bind(on_release=self.escolher_icone)

        self.add_widget(self.icon_display_image)
        self.add_widget(self.word_input)
        self.add_widget(self.icon_button)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def escolher_icone(self, instance):
        arquivos = [f for f in os.listdir(PASTA_EMOJIS) if f.endswith(".png")]
        content = GridLayout(cols=5, spacing=10, padding=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        for nome in arquivos:
            caminho = os.path.join(PASTA_EMOJIS, nome)
            btn = Button(background_normal=caminho, size=(60, 60), size_hint=(None, None))
            btn.bind(on_release=lambda btn, c=caminho: self.selecionar_icone(c))
            content.add_widget(btn)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(content)

        self.popup = Popup(title="Escolha um ícone", content=scroll, size_hint=(0.8, 0.6))
        self.popup.open()

    def selecionar_icone(self, caminho):
        self.icon_display_image.source = caminho
        self.icon_display_image.reload()
        self.icone_path = caminho
        if hasattr(self, 'popup'):
            self.popup.dismiss()

    def get_texto(self):
        return f"{self.word_input.text} {os.path.basename(self.icone_path) if self.icone_path else ''}"

    def get_icone_path(self):
        return self.icone_path


class EscrevilandiaApp(App):
    def build(self):
        Window.clearcolor = (0.85, 0.92, 1, 1)
        self.root_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        titulo = Label(text="Escrevilândia: A terra da escrita", font_size=28, size_hint_y=None, height=50, color=(0, 0, 0, 1))
        self.root_layout.add_widget(titulo)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))

        self.itens = []
        for i in range(1, 5):
            item = PalavraEmoji(i)
            self.container.add_widget(item)
            self.itens.append(item)

        self.scroll.add_widget(self.container)
        self.root_layout.add_widget(self.scroll)

        botoes_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        salvar_btn = CustomButton(text="Salvar")
        salvar_btn.bind(on_release=self.salvar_palavras)
        botoes_layout.add_widget(salvar_btn)

        proximo_btn = CustomButton(text="Seguir")
        proximo_btn.bind(on_release=self.ir_para_proximo)
        botoes_layout.add_widget(proximo_btn)

        self.root_layout.add_widget(botoes_layout)
        return self.root_layout

    def salvar_palavras(self, instance):
        dados = []
        for item in self.itens:
            palavra = item.word_input.text.strip()
            icone = item.get_icone_path()
            if palavra:
                dados.append({"palavra": palavra, "icone": icone})

        try:
            with open(ARQUIVO_PALAVRAS, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            mensagem = f"Palavras e ícones salvos com sucesso em:\n{ARQUIVO_PALAVRAS}"
        except Exception as e:
            mensagem = f"Erro ao salvar: {e}"

        layout = BoxLayout(orientation='vertical', padding=20)
        with layout.canvas.before:
            Color(0.85, 0.92, 1, 1)
            bg = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[15])
        layout.bind(size=lambda inst, val: setattr(bg, 'size', val))
        layout.bind(pos=lambda inst, val: setattr(bg, 'pos', val))

        label = Label(text=mensagem, color=(0, 0, 1, 1))
        layout.add_widget(label)

        Popup(title="Salvar Palavras", content=layout, size_hint=(0.7, 0.3)).open()

    def ir_para_proximo(self, instance):
        layout = BoxLayout(orientation='vertical', padding=20)
        with layout.canvas.before:
            Color(0.85, 0.92, 1, 1)
            bg = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[15])
        layout.bind(size=lambda inst, val: setattr(bg, 'size', val))
        layout.bind(pos=lambda inst, val: setattr(bg, 'pos', val))
        label = Label(text="Você seguiu em frente!", color=(0, 0, 1, 1))
        layout.add_widget(label)
        Popup(title="Próximo Passo", content=layout, size_hint=(0.7, 0.3)).open()

    def carregar_palavras_salvas(self):
        if not os.path.exists(ARQUIVO_PALAVRAS):
            return

        try:
            with open(ARQUIVO_PALAVRAS, "r", encoding="utf-8") as f:
                dados = json.load(f)
            for item, entrada in zip(self.itens, dados):
                item.word_input.text = entrada.get("palavra", "")
                icone_caminho = entrada.get("icone", "")
                if icone_caminho and os.path.exists(icone_caminho):
                    item.icon_display_image.source = icone_caminho
                    item.icon_display_image.reload()
                    item.icone_path = icone_caminho
        except Exception as e:
            print(f"[Erro ao carregar JSON]: {e}")


if __name__ == '__main__':
    app = EscrevilandiaApp()
    app.run()
