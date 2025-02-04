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
            lag_ratio = 0.5
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
            lag_ratio = 0.5
        )

class ListeningKernel(VGroup):
    def __init__(self, port, height, width, **kwargs):
        super().__init__(**kwargs)

        self.rect = Rectangle(height=height, width=width, color=GREY).to_edge(LEFT)
        
        self.syn_queue = Queue("SYN队列", height=height * 0.6, width= width * 0.2,color=BLUE)
        self.acc_queue = Queue("ACCEPT队列", height=height * 0.6, width= width * 0.2,color=GREEN)

        # 并排两个队列
        queues = VGroup(self.acc_queue, self.syn_queue).arrange(RIGHT, buff=0.5)

        self.port = CircleText("端口:" + port, RED, 0.3, 26)

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
        self.text = Text("Server").next_to(self.rect, DOWN)
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
        self.text = Text("Client").next_to(self.rect, DOWN)
        self.add(self.rect, self.text)

    def animate_creation(self):
        return AnimationGroup(
            Create(self.rect),
            Write(self.text),
        )

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
        server_proc = ServerProc(1, 4, WHITE)
        server_kernel = ListeningKernel("8080", 6, 4).next_to(server_proc, DOWN, buff=1)

        VGroup(
            server_proc,
            server_kernel,
        ).arrange(DOWN, buff=0.5).to_edge(LEFT)

        client = Client(2, 4, GREY).to_edge(RIGHT)

        self.play(
            server_kernel.animate_creation(),
            server_proc.animate_creation(),
            client.animate_creation(),
        )

    def constructA(self):
        self.create_server_proc()
        self.play(FadeIn(self.server_proc))
        # 创建服务器和客户端图示
        server = Rectangle(height=3, width=2, color=BLUE).to_edge(LEFT)

        client = Rectangle(height=3, width=2, color=GREEN).to_edge(RIGHT)
        client_text = Text("Client").next_to(client, DOWN)

        # 创建两个队列
        syn_queue = Rectangle(height=2, width=1.5, color=RED).next_to(self.server_proc, UP+RIGHT)
        accept_queue = Rectangle(height=2, width=1.5, color=YELLOW).next_to(syn_queue, RIGHT)
        queue_labels = VGroup(
            Text("SYN队列").scale(0.5).next_to(syn_queue, UP),
            Text("ACCEPT队列").scale(0.5).next_to(accept_queue, UP)
        )

        # 创建状态文本
        state_text = Text("", font_size=24).to_edge(UP)

        # 初始化场景
        self.play(
            Create(self.server_proc),
            Create(client),
            Write(client_text),
            run_time=2
        )
        self.wait(1)
        self.play(
            Create(syn_queue),
            Create(accept_queue),
            Write(queue_labels),
            run_time=2
        )

        # 第一次握手 (SYN)
        self.add_state("第一次握手: SYN →")
        syn_packet = self.create_packet("SYN", client, server)
        self.play(
            syn_packet.animate.move_to(server.get_center()),
            run_time=2
        )
        self.play(FadeOut(syn_packet))
        syn_item = self.add_to_queue(syn_queue, "SYN#1")

        # 第二次握手 (SYN-ACK)
        self.add_state("第二次握手: SYN-ACK ←")
        syn_ack_packet = self.create_packet("SYN-ACK", server, client)
        self.play(
            syn_ack_packet.animate.move_to(client.get_center()),
            run_time=2
        )
        self.play(FadeOut(syn_ack_packet))

        # 第三次握手 (ACK)
        self.add_state("第三次握手: ACK →")
        ack_packet = self.create_packet("ACK", client, server)
        self.play(
            ack_packet.animate.move_to(server.get_center()),
            run_time=2
        )
        self.play(FadeOut(ack_packet))

        # 移动到ACCEPT队列
        self.add_state("连接进入ACCEPT队列")
        moving_item = syn_item.copy()
        self.play(
            moving_item.animate.move_to(accept_queue.get_center()),
            FadeOut(syn_item),
            run_time=2
        )
        accept_item = self.add_to_queue(accept_queue, "Conn#1")

        # ACCEPT操作
        self.add_state("调用accept()取出连接")
        self.play(
            accept_item.animate.move_to(server.get_center()).scale(1.5),
            run_time=2
        )
        self.play(FadeOut(accept_item))

        self.wait(2)

    def create_packet(self, text, start, end):
        packet = VGroup(
            Rectangle(height=1, width=2, color=WHITE),
            Text(text, font_size=24)
        )
        packet.move_to(start.get_center())
        return packet

    def add_to_queue(self, queue, text):
        item = Text(text, font_size=20)
        item.move_to(queue.get_center())
        self.play(FadeIn(item))
        return item

    def add_state(self, text):
        new_text = Text(text, font_size=24).to_edge(UP)
        self.play(Transform(self.state_text, new_text))
        self.wait(0.5)