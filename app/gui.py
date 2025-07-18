import sys
import os
import json
import random
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QTextEdit, QTabWidget, QWidget
)
from PySide6.QtGui import QIcon, QClipboard
from PySide6.QtCore import Qt
from rsa_keygen import generate_rsa_keypair

# Simple lists for random name generation (Docker style)
ADJECTIVES = [
    "brave", "clever", "eager", "fancy", "gentle", "happy", "jolly", "kind", "lucky", "mighty",
    "nice", "proud", "quick", "silly", "witty", "zealous", "bold", "calm", "daring", "elegant"
]
NOUNS = [
    "lion", "tiger", "bear", "wolf", "fox", "eagle", "hawk", "shark", "whale", "otter",
    "panda", "koala", "falcon", "owl", "lynx", "bison", "moose", "rabbit", "deer", "seal"
]

def random_docker_name():
    return f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}"

class KeyGenPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("RSA Key Pair Generation")
        layout = QVBoxLayout()

        # Key name
        name_layout = QHBoxLayout()
        name_label = QLabel("Key name:")
        self.name_input = QLineEdit()
        self.name_input.setText(random_docker_name())
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Output directory
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Output directory:")
        self.dir_input = QLineEdit()
        default_dir = os.path.abspath("output_keys")
        self.dir_input.setText(default_dir)
        self.dir_input.setReadOnly(True)
        dir_button = QPushButton("Select...")
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        layout.addLayout(dir_layout)

        # Remove Generate Keys button
        # self.generate_button = QPushButton("Generate Keys")
        # self.generate_button.clicked.connect(self.generate_keys)
        # layout.addWidget(self.generate_button)

        self.setLayout(layout)
        self.generated_key_name = None
        self.generated_public_key = None
        self.generated_priv_path = None
        self.generated_pub_path = None
        self.generated_private_key = None
        self.registerField("key_name*", self.name_input)
        self.registerField("output_dir*", self.dir_input)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select output directory")
        if dir_path:
            self.dir_input.setText(dir_path)

    def generate_keys(self):
        key_name = self.name_input.text().strip()
        output_dir = self.dir_input.text().strip()
        if not key_name or not output_dir:
            QMessageBox.warning(self, "Required fields", "Please enter the key name and select the output directory.")
            return False
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            priv_path, pub_path = generate_rsa_keypair(key_name, output_dir)
            self.generated_key_name = key_name
            self.generated_priv_path = priv_path
            self.generated_pub_path = pub_path
            with open(pub_path, 'r') as f:
                self.generated_public_key = f.read()
            with open(priv_path, 'r') as f:
                self.generated_private_key = f.read()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the keys:\n{e}")
            return False

    def validatePage(self):
        # Called when Next is clicked
        return self.generate_keys()

    def isComplete(self):
        # Always allow Next, validation is handled in validatePage
        return True

class DDLPage(QWizardPage):
    def __init__(self, keygen_page: KeyGenPage):
        super().__init__()
        self.setTitle("Results")
        self.keygen_page = keygen_page
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        # DDL Tab
        self.ddl_tab = QWidget()
        ddl_layout = QVBoxLayout()

        # User input
        user_layout = QHBoxLayout()
        user_label = QLabel("Target user:")
        self.user_input = QLineEdit()
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        ddl_layout.addLayout(user_layout)

        # DDL output
        self.ddl_edit = QTextEdit()
        self.ddl_edit.setReadOnly(True)
        ddl_layout.addWidget(self.ddl_edit)

        # Buttons (refresh and copy)
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_btn.setToolTip("Refresh DDL")
        self.refresh_btn.clicked.connect(self.generate_ddl)
        btn_layout.addWidget(self.refresh_btn)

        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_btn.setToolTip("Copy to clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn)

        ddl_layout.addLayout(btn_layout)
        self.ddl_tab.setLayout(ddl_layout)
        self.tabs.addTab(self.ddl_tab, "DDL")

        # Secret Tab
        self.secret_tab = QWidget()
        secret_layout = QVBoxLayout()
        self.secret_edit = QTextEdit()
        self.secret_edit.setReadOnly(True)
        secret_layout.addWidget(self.secret_edit)
        # Buttons (refresh and copy) for secret
        secret_btn_layout = QHBoxLayout()
        self.secret_refresh_btn = QPushButton()
        self.secret_refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.secret_refresh_btn.setToolTip("Refresh Secret")
        self.secret_refresh_btn.clicked.connect(self.generate_secret)
        secret_btn_layout.addWidget(self.secret_refresh_btn)

        self.secret_copy_btn = QPushButton()
        self.secret_copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        self.secret_copy_btn.setToolTip("Copy to clipboard")
        self.secret_copy_btn.clicked.connect(self.copy_secret_to_clipboard)
        secret_btn_layout.addWidget(self.secret_copy_btn)

        secret_layout.addLayout(secret_btn_layout)
        self.secret_tab.setLayout(secret_layout)
        self.tabs.addTab(self.secret_tab, "Secret")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def initializePage(self):
        # Set default user to key name
        self.user_input.setText(self.keygen_page.generated_key_name or "")
        self.generate_ddl()
        self.generate_secret()

    def generate_ddl(self):
        user = self.user_input.text().strip()
        pubkey = (self.keygen_page.generated_public_key or "").replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")
        pubkey = pubkey.strip()
        # Format SQL for readability
        ddl = (
            f"ALTER USER {user}\n"
            f"    SET RSA_PUBLIC_KEY = '{pubkey}'\n;"
        )
        self.ddl_edit.setPlainText(ddl)
        self.generate_secret()  # Update secret tab if user changes

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.ddl_edit.toPlainText(), QClipboard.Clipboard)
        QMessageBox.information(self, "Copied!", "DDL copied to clipboard.")

    def generate_secret(self):
        user = self.user_input.text().strip()
        privkey = self.keygen_page.generated_private_key or ""
        secret = {
            "user": user,
            "private_key_pem": privkey
        }
        pretty_json = json.dumps(secret, indent=2, sort_keys=True)
        self.secret_edit.setPlainText(pretty_json)

    def copy_secret_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.secret_edit.toPlainText(), QClipboard.Clipboard)
        QMessageBox.information(self, "Copied!", "Secret JSON copied to clipboard.")

def main():
    app = QApplication(sys.argv)
    wizard = QWizard()
    wizard.setWindowTitle("RSA 2048 Key Pair Generator Wizard")
    keygen_page = KeyGenPage()
    ddl_page = DDLPage(keygen_page)
    wizard.addPage(keygen_page)
    wizard.addPage(ddl_page)
    wizard.setOption(QWizard.NoBackButtonOnStartPage, True)
    wizard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 