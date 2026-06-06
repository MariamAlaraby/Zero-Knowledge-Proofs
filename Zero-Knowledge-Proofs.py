import sys
import math
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, QTabWidget, 
                             QTextEdit, QFrame, QSizePolicy, QCheckBox)
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QTimer


BG_COLOR = "#07090f"
PANEL_COLOR = "#0d1117"
ACCENT_COLOR = "#00f5c4"
ACCENT_2 = "#7b61ff"
WARN_COLOR = "#ffb300"
FAIL_COLOR = "#ff3d71"
HIDDEN_COLOR = "#2a3545"
TEXT_COLOR = "#e8edf5"
PALETTE = ['#00f5c4', '#7b61ff', '#ff6b6b']

class GraphWidget(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setMinimumSize(350, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.title = title
        self.nodes = []
        self.edges = []
        self.colors = []
        self.highlight_edge = None
        self.setStyleSheet(f"background-color: {PANEL_COLOR}; border: 1px solid #1e2a3a; border-radius: 12px;")

    def update_graph(self, nodes, edges, colors=None, highlight_edge=None):
        self.nodes = nodes
        self.edges = edges
        self.colors = colors if colors else [HIDDEN_COLOR] * len(nodes)
        self.highlight_edge = highlight_edge
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        

        painter.setPen(QPen(QColor("#556070")))
        painter.setFont(QFont("Consolas", 12, QFont.Bold))
        painter.drawText(0, 15, self.width(), 40, Qt.AlignHCenter | Qt.AlignTop, self.title)

        if not self.nodes:
            return


        cx = self.width() / 2
        cy = (self.height() + 40) / 2


        for u, v in self.edges:
            is_hl = self.highlight_edge and ((u == self.highlight_edge[0] and v == self.highlight_edge[1]) or 
                                             (v == self.highlight_edge[0] and u == self.highlight_edge[1]))
            pen = QPen(QColor(WARN_COLOR) if is_hl else QColor("#2a3a50"))
            pen.setWidth(4 if is_hl else 2)
            painter.setPen(pen)
            
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            
            painter.drawLine(int(x1 + cx), int(y1 + cy), int(x2 + cx), int(y2 + cy))


        for i, (x, y) in enumerate(self.nodes):
            color = self.colors[i]
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor(255, 255, 255, 60), 2))
            
            px, py = int(x + cx), int(y + cy)
            painter.drawEllipse(px - 20, py - 20, 40, 40)
            
            painter.setPen(QPen(Qt.white))
            painter.setFont(QFont("Consolas", 12, QFont.Bold))
            painter.drawText(px - 20, py - 20, 40, 40, Qt.AlignCenter, str(i + 1))


class StatBox(QFrame):
    def __init__(self, title, initial_value):
        super().__init__()
        self.setStyleSheet(f"background-color: #111823; border: 1px solid #1e2a3a; border-radius: 8px;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.val_label = QLabel(str(initial_value))
        self.val_label.setStyleSheet(f"color: {ACCENT_COLOR}; font-size: 24px; font-weight: bold; border: none;")
        self.val_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #556070; font-size: 11px; font-weight: bold; border: none; letter-spacing: 1px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.val_label)
        layout.addWidget(title_label)
        self.setFixedSize(135, 75)

    def update_val(self, val):
        self.val_label.setText(str(val))


class ZKPSimulatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zero Knowledge Proof Simulator")
        self.setGeometry(50, 50, 1400, 950)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR}; font-family: Consolas;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QVBoxLayout()
        title = QLabel("Zero Knowledge Proof Simulator")
        title.setStyleSheet(f"color: {ACCENT_COLOR}; font-size: 36px; font-weight: bold; padding-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("INTERACTIVE CRYPTOGRAPHIC PROTOCOL DEMONSTRATOR · GRAPH ISOMORPHISM & 3-COLORABILITY")
        subtitle.setStyleSheet("color: #556070; font-size: 14px; letter-spacing: 2px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(30)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #1e2a3a; border-radius: 10px; background: {PANEL_COLOR}; }}
            QTabBar::tab {{ background: {BG_COLOR}; color: #556070; padding: 15px 40px; font-size: 14px; font-weight: bold; border: 1px solid #1e2a3a; border-radius: 5px; margin-right: 10px; }}
            QTabBar::tab:selected {{ background: #1a2332; color: {ACCENT_COLOR}; border-color: {ACCENT_COLOR}; }}
        """)
        
        self.setup_3color_tab()
        self.setup_iso_tab()
        
        self.main_layout.addWidget(self.tabs)

    def calculate_nodes_offsets(self, n, r):
        nodes = []
        for i in range(n):
            ang = (2 * math.pi * i / n) - math.pi / 2
            nodes.append((r * math.cos(ang), r * math.sin(ang)))
        return nodes

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ================= 3-COLORABILITY LOGIC & UI =================
    def setup_3color_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        controls = QHBoxLayout()
        controls.setAlignment(Qt.AlignLeft)
        
        self.col_combo = QComboBox()
        self.col_combo.addItems(["Petersen-like (6-node)", "Triangle (3-node)", "Wheel (7-node)"])
        self.col_combo.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR}; border: 1px solid #556070; padding: 10px; font-size: 14px; border-radius: 5px; min-width: 200px;")
        
        self.col_cheat_checkbox = QCheckBox("Cheat Mode")
        self.col_cheat_checkbox.setStyleSheet(f"color: {FAIL_COLOR}; font-weight: bold; font-size: 14px; padding-left: 10px;")

        self.btn_load_col = QPushButton("⟳ LOAD GRAPH")
        self.btn_step_col = QPushButton("▶ ONE ROUND")
        self.btn_auto_col = QPushButton("⚡ AUTO 30 ROUNDS")
        
        self.btn_load_col.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: black; padding: 10px 20px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        self.btn_step_col.setStyleSheet(f"background-color: transparent; border: 1px solid {ACCENT_2}; color: {ACCENT_2}; padding: 10px 20px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        self.btn_auto_col.setStyleSheet(f"background-color: transparent; border: 1px solid {WARN_COLOR}; color: {WARN_COLOR}; padding: 10px 20px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        
        controls.addWidget(self.col_combo)
        controls.addWidget(self.col_cheat_checkbox)
        controls.addSpacing(20)
        controls.addWidget(self.btn_load_col)
        controls.addWidget(self.btn_step_col)
        controls.addWidget(self.btn_auto_col)
        layout.addLayout(controls)

        canvases = QHBoxLayout()
        self.graph_main = GraphWidget("GRAPH (COMMITTED — COLORS HIDDEN)")
        self.graph_reveal = GraphWidget("REVEALED EDGE (THIS ROUND)")
        canvases.addWidget(self.graph_main, 2)
        canvases.addWidget(self.graph_reveal, 1)
        layout.addLayout(canvases)

        stats_layout = QHBoxLayout()
        stats_layout.setAlignment(Qt.AlignLeft)
        self.col_stat_rounds = StatBox("ROUNDS", "0")
        self.col_stat_passed = StatBox("PASSED", "0")
        self.col_stat_failed = StatBox("FAILED", "0")
        self.col_stat_conf = StatBox("CONFIDENCE", "0%")
        self.col_stat_edges = StatBox("EDGES", "0")
        
        stats_layout.addWidget(self.col_stat_rounds)
        stats_layout.addWidget(self.col_stat_passed)
        stats_layout.addWidget(self.col_stat_failed)
        stats_layout.addWidget(self.col_stat_conf)
        stats_layout.addWidget(self.col_stat_edges)
        layout.addLayout(stats_layout)

        history_label = QLabel("ROUND HISTORY")
        history_label.setStyleSheet("color: #556070; font-size: 12px; font-weight: bold; letter-spacing: 1px; margin-top: 10px;")
        layout.addWidget(history_label)
        
        self.col_history_layout = QHBoxLayout()
        self.col_history_layout.setAlignment(Qt.AlignLeft)
        self.col_history_layout.setSpacing(5)
        
        history_widget = QWidget()
        history_widget.setLayout(self.col_history_layout)
        history_widget.setFixedHeight(40)
        layout.addWidget(history_widget)

        self.log_col = QTextEdit()
        self.log_col.setReadOnly(True)
        self.log_col.setStyleSheet(f"background-color: #040608; border: 1px solid #1e2a3a; font-size: 16px; padding: 10px; border-radius: 8px;")
        self.log_col.setMinimumHeight(150)
        layout.addWidget(self.log_col)

        self.tabs.addTab(tab, "🎨 3-COLORABILITY")

        self.btn_load_col.clicked.connect(self.init_3color)
        self.btn_step_col.clicked.connect(self.step_3color)
        self.col_combo.currentIndexChanged.connect(self.init_3color)
        
        self.col_timer = QTimer()
        self.col_timer.timeout.connect(self.step_3color)
        self.btn_auto_col.clicked.connect(self.toggle_auto_col)
        
        self.init_3color()

    def init_3color(self):
        self.col_rounds = 0
        self.col_passed = 0
        self.col_failed = 0
        self.log_col.clear()
        self.clear_layout(self.col_history_layout)
        
        sel = self.col_combo.currentIndex()
        if sel == 0: 
            self.col_edges = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,0), (0,3), (1,4), (2,5)]
            self.col_base_coloring = [0, 1, 2, 0, 1, 2]
            n = 6
        elif sel == 1: 
            self.col_edges = [(0,1), (1,2), (0,2)]
            self.col_base_coloring = [0, 1, 2]
            n = 3
        else: 
            self.col_edges = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,0), (6,0), (6,1), (6,2), (6,3), (6,4), (6,5)]
            self.col_base_coloring = [0, 1, 0, 1, 0, 1, 2]
            n = 7
            
        r = 110
        self.col_nodes = self.calculate_nodes_offsets(n, r)
        self.graph_main.update_graph(self.col_nodes, self.col_edges)
        self.graph_reveal.update_graph([], [])
        
        self.update_col_stats()
        self.log_col.append(f"<span style='color:{ACCENT_COLOR}'>[SYSTEM] Loaded {self.col_combo.currentText()}. Prover has valid coloring (Hidden).</span>")

    def step_3color(self):
        if self.col_rounds >= 30 and self.col_timer.isActive():
            self.toggle_auto_col()
            return
            
        self.col_rounds += 1
        
        perm = [0, 1, 2]
        random.shuffle(perm)
        perm_coloring = [perm[c] for c in self.col_base_coloring]

        edge_idx = random.randint(0, len(self.col_edges) - 1)
        u, v = self.col_edges[edge_idx]

        color_u = perm_coloring[u]
        color_v = perm_coloring[v]
        
        if self.col_cheat_checkbox.isChecked() and random.random() < 0.5:
            color_v = color_u

        pass_check = color_u != color_v

        reveal_colors = [HIDDEN_COLOR] * len(self.col_nodes)
        reveal_colors[u] = PALETTE[color_u]
        reveal_colors[v] = PALETTE[color_v]
        
        self.graph_main.update_graph(self.col_nodes, self.col_edges, reveal_colors, highlight_edge=(u, v))
        
        reveal_nodes = [(-60, 0), (60, 0)]
        self.graph_reveal.update_graph(reveal_nodes, [(0, 1)], [PALETTE[color_u], PALETTE[color_v]])

        color_names = ['CYAN', 'PURPLE', 'RED']
        
        self.log_col.append(f"<span style='color:#7a9ab0'>Round {self.col_rounds}: Verifier checks edge ({u+1}↔{v+1})</span>")
        
        if pass_check:
            self.col_passed += 1
            self.log_col.append(f"<span style='color:{ACCENT_COLOR}'>  ✓ Different colors - Node {u+1}: {color_names[color_u]}, Node {v+1}: {color_names[color_v]}</span><br>")
            self.add_col_history_dot(True)
        else:
            self.col_failed += 1
            self.log_col.append(f"<span style='color:{FAIL_COLOR}; font-weight: bold;'>  ✗ SAME COLOR CAUGHT - Cheater detected!</span><br>")
            self.add_col_history_dot(False)
            if self.col_timer.isActive():
                self.toggle_auto_col()
                
        self.update_col_stats()

    def update_col_stats(self):
        self.col_stat_rounds.update_val(self.col_rounds)
        self.col_stat_passed.update_val(self.col_passed)
        self.col_stat_failed.update_val(self.col_failed)
        self.col_stat_edges.update_val(len(self.col_edges))
        
        cheat_prob = (len(self.col_edges) - 1) / len(self.col_edges)
        conf = round((1 - math.pow(cheat_prob, self.col_rounds)) * 100, 2) if self.col_rounds > 0 else 0
        self.col_stat_conf.update_val(f"{conf}%")

    def add_col_history_dot(self, passed):
        dot = QFrame()
        dot.setFixedSize(24, 24)
        color = ACCENT_COLOR if passed else FAIL_COLOR
        dot.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        self.col_history_layout.addWidget(dot)

    def toggle_auto_col(self):
        if self.col_timer.isActive():
            self.col_timer.stop()
            self.btn_auto_col.setText("⚡ AUTO 30 ROUNDS")
        else:
            if self.col_rounds >= 30:
                self.init_3color()
            self.col_timer.start(300)
            self.btn_auto_col.setText("🛑 STOP AUTO")


    # ================= GRAPH ISOMORPHISM LOGIC & UI =================
    def setup_iso_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        controls = QHBoxLayout()
        controls.setAlignment(Qt.AlignLeft)
        
        self.iso_combo = QComboBox()
        self.iso_combo.addItems(["4-node graphs", "5-node graphs", "6-node graphs", "7-node graphs"])
        self.iso_combo.setCurrentIndex(1)
        self.iso_combo.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR}; border: 1px solid #556070; padding: 10px; font-size: 14px; border-radius: 5px; min-width: 150px;")
        
        self.iso_cheat_checkbox = QCheckBox("Cheat Mode")
        self.iso_cheat_checkbox.setStyleSheet(f"color: {FAIL_COLOR}; font-weight: bold; font-size: 14px; padding-left: 10px;")

        self.btn_load_iso = QPushButton("⟳ NEW GRAPHS")
        self.btn_step_iso = QPushButton("▶ ONE ROUND")
        self.btn_auto_iso = QPushButton("⚡ AUTO 20 ROUNDS")
        
        self.btn_load_iso.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: black; padding: 10px 20px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        self.btn_step_iso.setStyleSheet(f"background-color: transparent; border: 1px solid {ACCENT_2}; color: {ACCENT_2}; padding: 10px 20px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        self.btn_auto_iso.setStyleSheet(f"background-color: transparent; border: 1px solid {WARN_COLOR}; color: {WARN_COLOR}; padding: 10px 20px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        
        controls.addWidget(self.iso_combo)
        controls.addWidget(self.iso_cheat_checkbox)
        controls.addSpacing(10)
        controls.addWidget(self.btn_load_iso)
        controls.addWidget(self.btn_step_iso)
        controls.addWidget(self.btn_auto_iso)
        layout.addLayout(controls)

        canvases = QHBoxLayout()
        self.graph_g = GraphWidget("GRAPH G (PUBLIC)")
        self.graph_h = GraphWidget("GRAPH H (PUBLIC)")
        self.graph_hp = GraphWidget("H' COMMITMENT (THIS ROUND)")
        canvases.addWidget(self.graph_g)
        canvases.addWidget(self.graph_h)
        canvases.addWidget(self.graph_hp)
        layout.addLayout(canvases)

        stats_layout = QHBoxLayout()
        stats_layout.setAlignment(Qt.AlignLeft)
        self.iso_stat_rounds = StatBox("ROUNDS", "0")
        self.iso_stat_passed = StatBox("PASSED", "0")
        self.iso_stat_failed = StatBox("FAILED", "0")
        self.iso_stat_conf = StatBox("CONFIDENCE", "0%")
        stats_layout.addWidget(self.iso_stat_rounds)
        stats_layout.addWidget(self.iso_stat_passed)
        stats_layout.addWidget(self.iso_stat_failed)
        stats_layout.addWidget(self.iso_stat_conf)
        layout.addLayout(stats_layout)

        iso_history_label = QLabel("ROUND HISTORY")
        iso_history_label.setStyleSheet("color: #556070; font-size: 12px; font-weight: bold; letter-spacing: 1px; margin-top: 10px;")
        layout.addWidget(iso_history_label)
        
        self.iso_history_layout = QHBoxLayout()
        self.iso_history_layout.setAlignment(Qt.AlignLeft)
        self.iso_history_layout.setSpacing(5)
        
        iso_history_widget = QWidget()
        iso_history_widget.setLayout(self.iso_history_layout)
        iso_history_widget.setFixedHeight(40)
        layout.addWidget(iso_history_widget)

        self.log_iso = QTextEdit()
        self.log_iso.setReadOnly(True)
        self.log_iso.setStyleSheet(f"background-color: #040608; border: 1px solid #1e2a3a; font-size: 16px; padding: 10px; border-radius: 8px;")
        self.log_iso.setMinimumHeight(150)
        layout.addWidget(self.log_iso)

        self.tabs.addTab(tab, "🔁 GRAPH ISOMORPHISM")

        self.btn_load_iso.clicked.connect(self.init_iso)
        self.btn_step_iso.clicked.connect(self.step_iso)
        self.iso_combo.currentIndexChanged.connect(self.init_iso)
        
        self.iso_timer = QTimer()
        self.iso_timer.timeout.connect(self.step_iso)
        self.btn_auto_iso.clicked.connect(self.toggle_auto_iso)

        self.init_iso()

    def init_iso(self):
        self.iso_rounds = 0
        self.iso_passed = 0
        self.iso_failed = 0
        self.log_iso.clear()
        self.clear_layout(self.iso_history_layout)
        self.update_iso_stats()
        
        n = int(self.iso_combo.currentText().split('-')[0])
        r = 90
        self.iso_nodes = self.calculate_nodes_offsets(n, r)
        
        self.g_edges = [(i, (i+1)%n) for i in range(n)]
        extra = random.randint(0, n-2)
        for _ in range(extra):
            a = random.randint(0, n-1)
            b = (a + 2 + random.randint(0, n-3)) % n
            if (a, b) not in self.g_edges and (b, a) not in self.g_edges:
                self.g_edges.append((a, b))
        
        self.secret_sigma = list(range(n))
        random.shuffle(self.secret_sigma)
        self.h_edges = [(self.secret_sigma[u], self.secret_sigma[v]) for u, v in self.g_edges]

        self.graph_g.update_graph(self.iso_nodes, self.g_edges)
        self.graph_h.update_graph(self.iso_nodes, self.h_edges)
        self.graph_hp.update_graph([], [])
        
        self.log_iso.append(f"<span style='color:{ACCENT_COLOR}'>[SYSTEM] Generated Isomorphic Graphs G and H with {n} nodes.</span>")

    def step_iso(self):
        if self.iso_rounds >= 20 and self.iso_timer.isActive():
            self.toggle_auto_iso()
            self.log_iso.append(f"<br><span style='color:{ACCENT_COLOR}; font-weight:bold;'>[SUCCESS] PROOF ACCEPTED - Knowledge verified with >99.9999% confidence!</span>")
            return

        self.iso_rounds += 1
        n = len(self.iso_nodes)

        tau = list(range(n))
        random.shuffle(tau)
        hp_edges = [(tau[u], tau[v]) for u, v in self.g_edges]
        self.graph_hp.update_graph(self.iso_nodes, hp_edges)

        challenge = random.choice([0, 1])

        target = "G -> H'" if challenge == 0 else "H -> H'"
        
        pass_check = True
        if self.iso_cheat_checkbox.isChecked() and random.random() < 0.5:
            pass_check = False

        self.log_iso.append(f"<span style='color:#7a9ab0'>Round {self.iso_rounds}: Verifier challenges: show mapping for {target}</span>")
        
        if pass_check:
            self.iso_passed += 1
            self.log_iso.append(f"<span style='color:{ACCENT_COLOR}'>  Prover reveals correct mapping ✓</span><br>")
            self.add_iso_history_dot(True)
        else:
            self.iso_failed += 1
            self.log_iso.append(f"<span style='color:{FAIL_COLOR}; font-weight: bold;'>  ✗ CHEATER CAUGHT - Unable to provide valid mapping!</span><br>")
            self.add_iso_history_dot(False)
            if self.iso_timer.isActive():
                self.toggle_auto_iso()
                
        self.update_iso_stats()

    def update_iso_stats(self):
        self.iso_stat_rounds.update_val(self.iso_rounds)
        self.iso_stat_passed.update_val(self.iso_passed)
        self.iso_stat_failed.update_val(self.iso_failed)
        conf = round((1 - math.pow(0.5, self.iso_rounds)) * 100, 2) if self.iso_rounds > 0 else 0
        self.iso_stat_conf.update_val(f"{conf}%")

    def add_iso_history_dot(self, passed):
        dot = QFrame()
        dot.setFixedSize(24, 24)
        color = ACCENT_COLOR if passed else FAIL_COLOR
        dot.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        self.iso_history_layout.addWidget(dot)

    def toggle_auto_iso(self):
        if self.iso_timer.isActive():
            self.iso_timer.stop()
            self.btn_auto_iso.setText("⚡ AUTO 20 ROUNDS")
        else:
            if self.iso_rounds >= 20:
                self.init_iso()
            self.iso_timer.start(300)
            self.btn_auto_iso.setText("🛑 STOP AUTO")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ZKPSimulatorApp()
    window.show()
    sys.exit(app.exec_())