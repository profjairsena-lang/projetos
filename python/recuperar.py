import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

ARQUIVO_ICONES = "icones.txt"
PASTA_EMOJIS = os.path.join(os.path.dirname(__file__), "emojis")


class IconeApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.img_icone = Image(size_hint_y=None, height=120)
        self.layout.add_widget(self.img_icone)

        self.btn_escolher = Button(text="Escolher ícone", size_hint_y=None, height=50)
        self.btn_escolher.bind(on_release=self.abrir_popup_icones)
        self.layout.add_widget(self.btn_escolher)

        self.btn_salvar = Button(text="Salvar ícone", size_hint_y=None, height=50)
        self.btn_salvar.bind(on_release=self.salvar_icone)
        self.layout.add_widget(self.btn_salvar)

        self.btn_resgatar = Button(text="Resgatar ícone salvo", size_hint_y=None, height=50)
        self.btn_resgatar.bind(on_release=self.resgatar_icone)
        self.layout.add_widget(self.btn_resgatar)

        self.label_status = Label(text="", size_hint_y=None, height=40)
        self.layout.add_widget(self.label_status)

        self.icone_escolhido = None
        return self.layout

    def abrir_popup_icones(self, instance):
        arquivos = [f for f in os.listdir(PASTA_EMOJIS) if f.endswith('.png')]
        grid = GridLayout(cols=5, spacing=10, padding=10)

        for nome in arquivos:
            caminho = os.path.join(PASTA_EMOJIS, nome)
            img_btn = Button(background_normal=caminho, size_hint=(None, None), size=(60, 60))
            img_btn.bind(on_release=lambda btn, c=caminho: self.selecionar_icone(c))
            grid.add_widget(img_btn)

        popup = Popup(title="Escolha um ícone", content=grid, size_hint=(None, None), size=(400, 300))
        self._popup_icones = popup
        popup.open()

    def selecionar_icone(self, caminho):
        self.icone_escolhido = caminho
        self.img_icone.source = caminho
        self.label_status.text = "Ícone selecionado"
        if hasattr(self, '_popup_icones'):
            self._popup_icones.dismiss()

    def salvar_icone(self, instance):
        if self.icone_escolhido:
            with open(ARQUIVO_ICONES, "w", encoding="utf-8") as f:
                f.write(self.icone_escolhido)
            self.label_status.text = "Ícone salvo com sucesso!"
        else:
            self.label_status.text = "Selecione um ícone primeiro."

    def resgatar_icone(self, instance):
        if os.path.exists(ARQUIVO_ICONES):
            with open(ARQUIVO_ICONES, "r", encoding="utf-8") as f:
                caminho = f.read().strip()
            if os.path.exists(caminho):
                self.img_icone.source = caminho
                self.label_status.text = "Ícone carregado!"
            else:
                self.label_status.text = "Arquivo de ícone não encontrado!"
        else:
            self.label_status.text = "Nenhum ícone salvo ainda."

if __name__ == '__main__':
    IconeApp().run()
