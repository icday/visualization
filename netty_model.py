from manim import *

class NettyThreadModel(Scene):
    def construct(self):
        # 颜色定义
        boss_color = BLUE
        worker_color = GREEN
        io_color = YELLOW
        business_color = ORANGE
        
        # 创建服务器主体
        server_box = RoundedRectangle(corner_radius=0.5, height=4, width=6, fill_color=WHITE, fill_opacity=0.1)
        server_label = Text("Netty Server", font_size=24).next_to(server_box, UP)

        # 创建BossGroup
        boss_group = VGroup(*[
            Circle(0.3, color=boss_color, fill_opacity=0.5).set_fill(boss_color)
            for _ in range(1)  # BossGroup通常只有1个线程
        ]).arrange(RIGHT, buff=0.2)
        boss_label = Text("BossGroup", color=boss_color, font_size=20).next_to(boss_group, UP)
        
        # 创建WorkerGroup
        worker_group = VGroup(*[
            Circle(0.3, color=worker_color, fill_opacity=0.5).set_fill(worker_color)
            for _ in range(3)  # 假设有3个Worker线程
        ]).arrange(RIGHT, buff=0.2)
        worker_label = Text("WorkerGroup", color=worker_color, font_size=20).next_to(worker_group, UP)
        
        # 将组件放入服务器
        groups = VGroup(boss_group, worker_group).arrange(DOWN, buff=1.5)
        groups.move_to(server_box.get_center())
        server = VGroup(server_box, server_label, groups, boss_label, worker_label)

        # 创建客户端
        client = VGroup(
            RoundedRectangle(corner_radius=0.3, height=1.5, width=2, fill_color=WHITE, fill_opacity=0.1),
            Text("Client", font_size=20)
        ).arrange(DOWN, buff=0.2).shift(LEFT*4)
        
        self.play(Create(server), Create(client))
        self.wait(1)

        # 显示连接建立过程
        connection_line = DashedLine(client.get_right(), server_box.get_left(), color=GREY)
        connection_label = Text("New Connection", font_size=18, color=GREY_B).next_to(connection_line, UP)
        
        self.play(
            Create(connection_line),
            Write(connection_label)
        )
        self.wait(0.5)

        # 展示BossGroup处理新连接
        boss_thread = boss_group[0].copy()
        self.play(
            boss_thread.animate.scale(1.2).set_color(WHITE),
            Indicate(boss_group[0], color=WHITE)
        )
        
        # 转移连接到WorkerGroup
        worker_thread = worker_group[1].copy()  # 选择第二个worker线程
        registration_arrow = CurvedArrow(
            boss_thread.get_right(),
            worker_thread.get_left(),
            color=worker_color,
            angle=-TAU/4
        )
        
        self.play(
            boss_thread.animate.move_to(registration_arrow.get_start()),
            Create(registration_arrow),
            worker_thread.animate.move_to(registration_arrow.get_end()).scale(1.2),
        )
        self.wait(1)

        # 客户端发送请求
        request_text = Text("Hello!", font_size=18).next_to(client, UP)
        request_arrow = Arrow(
            client.get_top(),
            server_box.get_bottom(),
            color=io_color,
            buff=0.2,
            max_tip_length_to_length_ratio=0.1
        )
        
        self.play(
            Write(request_text),
            GrowArrow(request_arrow)
        )
        self.wait(0.5)

        # 展示Worker处理IO事件
        io_event_box = SurroundingRectangle(worker_thread, color=io_color, buff=0.15)
        self.play(
            Create(io_event_box),
            worker_thread.animate.set_color(io_color)
        )
        
        # 业务线程处理（假设有业务线程池）
        business_thread = Circle(0.3, color=business_color, fill_opacity=0.5
                                ).set_fill(business_color).shift(RIGHT*3)
        business_arrow = Arrow(
            worker_thread.get_right(),
            business_thread.get_left(),
            color=business_color
        )
        
        self.play(
            Create(business_thread),
            Create(business_arrow),
            worker_thread.animate.set_color(worker_color),
            Uncreate(io_event_box)
        )
        self.wait(0.5)

        # 返回响应
        response_arrow = Arrow(
            server_box.get_bottom(),
            client.get_top(),
            color=GREEN,
            buff=0.2,
            max_tip_length_to_length_ratio=0.1
        )
        response_text = Text("Hello!", font_size=18).next_to(response_arrow, RIGHT)
        
        self.play(
            ReplacementTransform(request_arrow, response_arrow),
            ReplacementTransform(request_text, response_text)
        )
        self.wait(1)

        # 清理动画
        self.play(
            FadeOut(response_arrow),
            FadeOut(response_text),
            FadeOut(business_thread),
            FadeOut(business_arrow),
            FadeOut(registration_arrow),
            FadeOut(boss_thread),
            FadeOut(worker_thread)
        )
        self.wait(1)
