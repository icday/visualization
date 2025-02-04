from manim import *

class UserKernelSpace(Scene):
    def construct(self):
        # 颜色方案
        user_color = BLUE
        kernel_color = RED
        line_color = WHITE

        # 创建主容器
        main_rect = Rectangle(
            height=6, width=10, 
            color=line_color, 
            stroke_width=2
        ).to_edge(UP)

        # 添加水平分隔线（用户空间和内核空间）
        separator = Line(
            main_rect.get_left(), main_rect.get_right(),
            color=line_color, stroke_width=1.5
        ).shift(DOWN * 2.5)

        # 添加空间标签
        user_label = Text("用户空间 (User Space)", font_size=24).set_color(user_color)
        kernel_label = Text("系统空间 (Kernel Space)", font_size=24).set_color(kernel_color)
        user_label.next_to(main_rect.get_top(), DOWN).shift(UP*0.5)
        kernel_label.next_to(separator, DOWN).shift(UP*0.5)

        # 用户空间组件
        user_components = VGroup(
            Text("应用程序", font_size=20),
            Text("标准库", font_size=20).next_to(user_label, DOWN).shift(DOWN),
            Text("运行时库", font_size=20).next_to(user_label, DOWN).shift(DOWN*2)
        ).arrange(DOWN, buff=0.6).move_to(main_rect).shift(UP*1.5)

        # 内核空间组件
        kernel_components = VGroup(
            Text("系统调用接口", font_size=20),
            Text("进程管理", font_size=20).next_to(separator, DOWN).shift(DOWN*0.5),
            Text("内存管理", font_size=20).next_to(separator, DOWN).shift(DOWN*1.5),
            Text("设备驱动", font_size=20).next_to(separator, DOWN).shift(DOWN*2.5)
        ).arrange(DOWN, buff=0.6)

        # 系统调用箭头
        syscall_arrow = Arrow(
            user_components[-1].get_bottom(),
            kernel_components[0].get_top(),
            color=YELLOW, buff=0.2,
            max_tip_length_to_length_ratio=0.15
        )
        syscall_label = Text("系统调用", font_size=20).next_to(syscall_arrow, RIGHT)

        # 动画序列
        self.play(Create(main_rect))
        self.play(Write(user_label), Write(kernel_label))
        self.play(Create(separator))
        
        # 绘制用户空间组件
        self.play(
            LaggedStart(
                *[FadeIn(comp, shift=UP) for comp in user_components],
                lag_ratio=0.3
            ),
            run_time=2
        )

        # 绘制内核空间组件
        self.play(
            LaggedStart(
                *[FadeIn(comp, shift=UP) for comp in kernel_components],
                lag_ratio=0.3
            ),
            run_time=2
        )

        # 展示系统调用
        self.play(
            GrowArrow(syscall_arrow),
            Write(syscall_label)
        )
        self.wait(2)

        # 高亮分隔线
        self.play(
            separator.animate.set_color(YELLOW).set_stroke_width(3),
            run_time=1.5
        )
        self.play(separator.animate.set_color(line_color).set_stroke_width(1.5))
        self.wait()

        # 最终展示
        final_group = VGroup(
            main_rect, separator, user_label, kernel_label,
            user_components, kernel_components,
            syscall_arrow, syscall_label
        )
        self.play(final_group.animate.scale(0.9).to_edge(LEFT))
        self.wait(2)