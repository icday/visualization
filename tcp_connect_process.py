from manim import *

class Queue(VGroup):
    def __init__(self, label_text, height, width, color, **kwargs):
        super().__init__(kwargs)
        self.queue = Rectangle(height=height, width=width, color=color)
        self.label = Text(label_text).scale(0.5).next_to(self.queue, UP)
        self.add(self.queue, self.label)

    def animate_creation(self):
        return AnimationGroup(
            Create(self.queue),
            Write(self.label),
        )

class CircleText(VGroup):
    def __init__(self, port, color, size, font_size, **kwargs):
        super().__init__(**kwargs)

        self.text = Text(port, font_size=font_size)

        self.circle = Circle(size, color=color, fill_opacity=0.5).next_to(self.text, LEFT)

        self.add(self.circle, self.text)

    def animate_creation(self):
        return AnimationGroup(
            Create(self.circle),
            Write(self.text),
        )

class ListeningKernel(VGroup):
    def __init__(self, port, height, width, **kwargs):
        super().__init__(**kwargs)

        self.rect = Rectangle(height=height, width=width, color=GREY).to_edge(LEFT)
        
        self.syn_queue = Queue("SYN队列", height=height * 0.6, width=width * 0.3,color=BLUE)
        self.acc_queue = Queue("ACCEPT队列", height=height * 0.6, width=width * 0.3,color=GREEN)

        # 并排两个队列
        queues = VGroup(self.acc_queue, self.syn_queue).arrange(RIGHT, buff=width * 0.05)

        self.port = CircleText("端口:" + port, RED, width * 0.05, 26)

        # 纵向排列队列组和端口
        VGroup(queues, self.port).arrange(DOWN, buff=0.5).move_to(self.rect.get_center())

        self.add(self.rect, self.syn_queue, self.acc_queue, self.port)

    def animate_creation(self):
        return AnimationGroup(
            Create(self.rect),
            self.syn_queue.animate_creation(),
            self.acc_queue.animate_creation(),
            Create(self.port)
        )


class ServerProc(VGroup):
    def __init__(self, height, width, color, **kwargs):
        super().__init__(**kwargs)

        self.rect = Rectangle(height=height, width=width, color=color)
        self.text = Text("Server").next_to(self.rect, UP)
        self.add(self.rect, self.text)

    def animate_creation(self):
        return AnimationGroup(
            Create(self.rect),
            Write(self.text),
        )

class Client(VGroup):
    def __init__(self, height, width, color, **kwargs):
        super().__init__(**kwargs)

        self.rect = Rectangle(height=height, width=width, color=color)
        self.text = Text("Client").next_to(self.rect, UP)
        self.add(self.rect, self.text)

    def animate_creation(self):
        return AnimationGroup(
            Create(self.rect),
            Write(self.text),
        )

class Connection(VGroup):
    def __init__(self, text, height, width, color, font_size, **kwargs):
        super().__init__(**kwargs)

        self.rect = Rectangle(height=height, width=width, color=color)
        self.text = Text(text, font_size=font_size).move_to(self.rect)
        self.add(self.rect, self.text)

class TCPConnectionProcess(Scene):
    state_text = Text("", font_size=24).to_edge(UP)

    server_proc = None

    def create_server_proc(self):
        server = Rectangle(height=2, width=4, color=BLUE).to_edge(LEFT)
        server_text = Text("Server Proc").next_to(server, DOWN)
        self.server_proc = VGroup(
            server, server_text
        )

    def construct(self):
        self.add_state("监听端口8088")

        server_proc = ServerProc(1, 4, WHITE)
        server_kernel = ListeningKernel("8088", 6, 4).next_to(server_proc, DOWN)

        VGroup(
            server_proc,
            server_kernel,
        ).arrange(DOWN).to_edge(LEFT)

        client = Client(2, 4, GREY).to_corner(DR)

        self.play(
            server_kernel.animate_creation(),
            server_proc.animate_creation(),
            client.animate_creation(),
        )

        self.add_state("第一次握手: SYN ←")
        syn_packet = self.create_packet("SYN", client)
        self.play(syn_packet.animate.scale(0.3).next_to(server_kernel.port.circle, LEFT, buff=0.15))
        self.play(FadeOut(syn_packet))

        conn = Connection("SYN-RECVD#1", 0.5, 1, BLUE, 10).move_to(server_kernel.syn_queue.get_bottom() + UP * 0.5)
        self.play(
            Create(conn)
        )

        self.add_state("第二次握手: SYN-ACK →")
        syn_ack_packet = self.create_packet("SYN-ACK", server_kernel.port).scale(0.3).next_to(server_kernel.port.circle, LEFT, buff=0.15)
        self.play(syn_ack_packet.animate.scale(3).move_to(client.rect))
        self.play(FadeOut(syn_ack_packet))

        self.add_state("第三次握手: ACK ←")
        ack_packet = self.create_packet("ACK", client)
        self.play(ack_packet.animate.scale(0.3).next_to(server_kernel.port.circle, LEFT, buff=0.15))
        self.play(FadeOut(ack_packet))

        acc_conn = Connection("ESTABLISHED", 0.5, 1, GREEN, 10).move_to(conn)
        self.play(ReplacementTransform(conn, acc_conn))
        self.play(acc_conn.animate.move_to(server_kernel.acc_queue.queue.get_top() + DOWN * 0.5))

        self.wait(5)

    def create_packet(self, text, start):
        packet = VGroup(
            Rectangle(height=1, width=2, color=WHITE),
            Text(text, font_size=24)
        )
        packet.move_to(start.get_center())
        return packet

    def add_to_queue(self, queue, text):
        item = Connection(text, 0.5, 1, WHITE, 10)
        item.move_to(queue.get_bottom() + UP * 0.5)
        self.play(FadeIn(item))
        return item

    def add_state(self, text):
        new_text = Text(text, font_size=24).to_edge(UP)
        self.play(Transform(self.state_text, new_text))
        self.wait(0.5)