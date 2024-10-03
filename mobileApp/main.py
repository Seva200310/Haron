from kivy.app import App
from kivy.uix.widget import Widget

from kivy.graphics import (Color,Ellipse,Rectangle,Line)
#if len(self.touch_points) == 2: с помощью этой штуки можно будет делать двухпальцевое масштабирование
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from math import sqrt
from kivy.uix.scatter import Scatter
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import DictProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
#from kivy.properties import BoolProperty
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.label import Label
import math
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
import socket
import requests
import json
import os

class Menu_Widget(BoxLayout):
    mode = StringProperty()
    scale = NumericProperty()

    

    def __init__(self,**kwargs):
        super(Menu_Widget,self).__init__(**kwargs)
        self.scale = 1
        #gl = GridLayout(cols = 1, pading = [30],spacing = [3])
        #bl = BoxLayout(orientation = "vertical")
        self.mode_list = ["moving","pikets","lines","view_point"]
        self.mode_index = 0
        self.mode = self.mode_list[self.mode_index]
        self.dawnscale_button = Button(text = "+")
        self.dawnscale_button.bind(on_press = self.downscale)
        self.upscale_button = Button(text = "-")
        self.upscale_button.bind(on_press = self.upscale)

        self.mode_button = Button(text = self.mode)
        self.mode_button.bind(on_press = self.change_mode)
        self.connect_button = Button(text = "connect")
        self.connect_button.bind(on_press = self.connect_to_device)
        self.delete_button = Button(text = "del")
        self.delete_button.bind(on_press = self.delete)
        self.add_widget((self.dawnscale_button))    
        self.add_widget((self.upscale_button))
        self.add_widget((self.mode_button))
        self.add_widget((self.connect_button))
        self.add_widget((self.delete_button))
        
    
    def change_mode(self,instance):
        self.mode_index+=1
        print(self.mode_index)
        self.mode_index%=len(self.mode_list)
        self.mode = self.mode_list[self.mode_index]
        self.mode_button.text = self.mode
    def connect_to_device(self,instance):
        pass
    def downscale(self,instance):
        print("downscaled")
        self.scale += 0.2
    def upscale(self,instance):
        print("upscaled")
        self.scale -= 0.2
    def delete(self,instance):
        self.parent.delete()
        

class PainterWidget(Widget):#Widget
    #moving_offsets = ListProperty()
    new_piket_pos = ListProperty()
    view_point_coords = ListProperty()
    offsets = ListProperty()
    def __init__(self,**kwargs):
        self.moving_touches = []
        self.mode = "moving"
        self.lines = []
        self.pikets_labels = []
        super(PainterWidget,self).__init__(**kwargs)
        self.new_line_points = []
        self.pikets = []
        #self.new_piket = []
        self.selected_lines = []
        self.selected_pikets = []
        self.selected_pikets_labels = []
        self.total_offset_x = 0
        self.total_offset_y = 0
        
        self.direction_line_exist = False
        with self.canvas:
                Color(0.5,0,0.5,1)
                self.view_point_coords = [300,300]
                self.view_point = Ellipse(pos = self.view_point_coords ,size = (20,20))
            #Ellipse(pos = (-10,0),size = (50,50))
            #self.lines.append(Line(points = [(100,100),(200,200)]))
        self.scale = 1
    #БЛОК КОСТЫЛЕЙ ДЛЯ ИСПРАВЛЕНИ БАГА С ОСТАТКАМИ ОКОШКА ВВОДА НАЗВАНИЯ ПИКЕТА
    
        
    def add_piket_name(self,piket_name,pos,size):
        #self.canvas.clear()
        #print(piket_name)
        #print(pos)
        #print(size)

        with self.canvas:
            Color(0,0,0,1)
            Rectangle(pos = [pos[0],pos[1]],size = size)
        #self.canvas.ask_update()
            #CoreLabel(text=piket_name, pos=pos, font_size=20)
            
                # Добавить Label в канвас
            #CoreLabel(text=piket_name, pos=pos, font_size=20)
            self.pikets.append(self.new_piket)
            self.new_pikets = []
            rendered_lines = []
            rendered_selected_lines = []
            rendered_pikets = []
            #Color(0.5,0,0.5,1)
            #self.view_point_coords = [200,200]
            #self.view_point = Ellipse(pos = self.view_point.pos ,size = (20,20))
            for line in self.lines:
                #rendered_line = line
                Color(0,1,0,1)
                self.canvas.remove(line)
                rendered_lines.append(Line(points = line.points))
            for selected_line in self.selected_lines:
                #rendered_s_line = selected_line
                Color(1,0,0,1)
                self.canvas.remove(selected_line)
                rendered_selected_lines.append(Line(points = selected_line.points))
            for piket in self.pikets:
                Color(0,0,1,1)
                #rendered_piket = piket
                self.canvas.remove(piket)
                rendered_pikets.append(Ellipse(pos = piket.pos,size = piket.size,index = 1))

            

            #print(len(rendered_lines))
            self.lines = rendered_lines
            self.selected_lines = rendered_selected_lines
            self.pikets = rendered_pikets
            rendered_lines = []
            rendered_selected_lines = []
            rendered_pikets = []
            self.pikets_labels.append(Label(text = piket_name,pos = [self.new_piket_pos[0]-25,self.new_piket_pos[1]-25],color = (0,0,1,1),halign = "left"))

    def make_survey(self,target_point_vec):
        

        with self.canvas:
            if self.direction_line_exist:
                self.canvas.remove(self.direction_line)
                self.canvas.remove(self.survey_point)
                self.direction_line_exist = False


            Color(0,0.5,0.5,1)
            point_pos = [self.view_point.pos[0]+target_point_vec[0]*self.scale,self.view_point.pos[1]+target_point_vec[1]*self.scale]
            self.direction_line =  Line(points = [self.view_point.pos[0]+10,self.view_point.pos[1]+10]+point_pos)      
            self.survey_point = Ellipse(pos = [point_pos[0]-5,point_pos[1]-5],size = (10,10),index = 1)
            

            if self.mode == "lines":
                self.new_line_points.append(point_pos)
                #print("new_line_point")
                if len(self.new_line_points) == 2:
                    Color(0,1,0,1)
                    self.lines.append(Line(points = self.new_line_points))
                    self.new_line_points = [self.new_line_points[-1]]


            self.direction_line_exist = True
            
    def check_collide_with_line(self,point1, point2, point3,tolerance = 5):

        # Угловой коэффициент
        if point2[0] - point1[0] == 0:  # Избегаем деления на ноль, если линия вертикальна
            m = float('inf')
        else:
            m = (point2[1] - point1[1]) / (point2[0] - point1[0])

        # Отрезок, отсекаемый прямой на оси y
        c = point1[1] - m * point1[0]

        # Вычислить расстояние от точки point3 до прямой
        distance = abs(m * point3[0] - point3[1] + c) / math.sqrt(m**2 + 1)
        #Вычисляем вычисляем расстояния от проверяемой точки до двух крайних точек отрезка,чтобы убедиться, что точка лежит в отрезке
        control_dist1 = ((point1[0]-point3[0])**2+(point1[1]-point3[1])**2)**0.5
        control_dist2 = ((point2[0]-point3[0])**2+(point2[1]-point3[1])**2)**0.5
        line_len = ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5

        # Если расстояние меньше или равно допуску, то точка принадлежит линии с учетом погрешности
        if distance <= tolerance and control_dist1<line_len and control_dist2<line_len:
            return True
        else:
            return False
    def check_collide_with_piket(self,piket,touch_pos):
        distance = ((piket.pos[0]-touch_pos[0])**2+(piket.pos[1]-touch_pos[1])**2)**0.5
        print(f"distance:{distance}")
        if distance <= piket.size[1]:
            return True
        else:
            return False
        
    def on_touch_down(self, touch):
        #print("touch")
        #print(self.mode)
        if self.mode == "view_point":
            with self.canvas:
                Color(0.5,0,0.5,1)
                self.view_point.pos = [touch.x,touch.y]
                self.view_point_coords = [touch.x,touch.y]

        if self.mode == "pikets":
            self.new_line_points = []
            if self.parent.piket_window == False:
                with self.canvas:
                    Color(0,0,1,1)
                    self.new_piket = Ellipse(pos = (touch.x-2,touch.y-2),size = (8,8),index = 0)
                    self.new_piket_pos = [touch.x,touch.y]

        elif self.mode == "lines":
            self.new_line_points.append([touch.x,touch.y])
            with self.canvas:
                Color(0,1,0,1)
                if len(self.new_line_points) == 2:
                    self.lines.append(Line(points = self.new_line_points))
                    self.new_line_points = []
                #elif len(self.new_line_points) > 2:
                    #self.lines[-1].points = self.new_line_points

        elif self.mode == "moving":
            self.new_line_points = []
            lines = []
            pikets = []
            pikets_labels = []
            #selected_lines = []
            with self.canvas:
                for line in self.lines:
                    if self.check_collide_with_line([line.points[0],line.points[1]],[line.points[2],line.points[3]],[touch.x,touch.y]):
                        Color(1,0,0,1)
                        self.selected_lines.append(Line(points = line.points))
                        self.canvas.remove(line)
                        #print("линия отмечена")
                    else:
                        Color(0,1,0,1)
                        lines.append(line)

                for i in range(len(self.pikets)):
                    if self.check_collide_with_piket(self.pikets[i],[touch.x,touch.y]):
                        print("touched")
                        Color(1,0,0,1)
                        self.selected_pikets.append(Ellipse(pos = self.pikets[i].pos,size = (8,8),index = 0))
                        self.canvas.remove(self.pikets[i])
                        self.pikets_labels[i].color = (1,0,0,1)
                        self.selected_pikets_labels.append(self.pikets_labels[i])
                    else:
                        print("dont touched")
                        Color(0,0,1,1)
                        pikets.append(Ellipse(pos = self.pikets[i].pos,size = (8,8),index = 0))
                        self.canvas.remove(self.pikets[i])
                        pikets_labels.append(self.pikets_labels[i])

                print("количество пикетов")
                print(len(pikets))
                print(len(self.selected_pikets))
                self.lines = lines
                self.pikets = pikets
                self.pikets_labels = pikets_labels


                #self.selected_lines = selected_lines
                #print(len(self.selected_lines))

            
        #self.line.points += (touch.x,touch.y)
       #return super().on_touch_down(touch)


    def on_touch_move(self, touch):
        self.moving_touches.append((touch.x,touch.y))
        if len(self.moving_touches) == 2:
            x_offset = self.moving_touches[1][0]-self.moving_touches[0][0]
            y_offset = self.moving_touches[1][1]-self.moving_touches[0][1]
            self.total_offset_x += x_offset
            self.total_offset_y += y_offset
            if (x_offset**2+y_offset**2)**0.5<50:
                self.offsets = [x_offset,y_offset] 
            else:
                x_offset = 0 
                y_offset = 0
                self.offsets = [0,0] 
            
            #self.moving_offsets = [x_offset,y_offset]
            #print(touch.x)
            for i in range(len(self.lines)):
                points = self.lines[i].points
                for j in range(0,len(points)-1,2):
                    points[j] += x_offset
                    points[j+1] += y_offset
                self.lines[i].points = points

            for i in range(len(self.selected_lines)):
                points = self.selected_lines[i].points
                #print(points)
                for j in range(0,len(points)-1,2):
                    points[j] += x_offset
                    points[j+1] += y_offset
                self.selected_lines[i].points = points

            self.view_point.pos = [self.view_point.pos[0]+x_offset,self.view_point.pos[1]+y_offset]
            #self.view_point_coords = self.view_point.pos

            for i in range(len(self.pikets)):
                piket_pos = list(self.pikets[i].pos)
                piket_pos[0] += x_offset
                piket_pos[1] += y_offset
                self.pikets[i].pos = piket_pos
                label_pos = list(self.pikets_labels[i].pos)
                label_pos[0] += x_offset
                label_pos[1] += y_offset
                self.pikets_labels[i].pos = label_pos
            
            for i in range(len(self.selected_pikets)):
                piket_pos = list(self.selected_pikets[i].pos)
                piket_pos[0] += x_offset
                piket_pos[1] += y_offset
                self.selected_pikets[i].pos = piket_pos
                label_pos = list(self.selected_pikets_labels[i].pos)
                label_pos[0] += x_offset
                label_pos[1] += y_offset
                self.selected_pikets_labels[i].pos = label_pos

            self.moving_touches = []

        #self.line.points = 
        #return super().on_touch_move(touch)
    def change_scale(self):
            #self.moving_offsets = [x_offset,y_offset]
            #print(touch.x)
            self.view_point.pos = [self.view_point_coords[0]*self.scale,self.view_point_coords[1]*self.scale]
            #self.view_point_coords = self.view_point.pos
            for i in range(len(self.lines)):
                points = self.lines[i].points
                for j in range(0,len(points)-1,2):
                    points[j] *= self.scale
                    points[j+1] *= self.scale
                self.lines[i].points = points

            for i in range(len(self.selected_lines)):
                points = self.selected_lines[i].points
                #print(points)
                for j in range(0,len(points)-1,2):
                    points[j] *= self.scale
                    points[j+1] *= self.scale
                self.selected_lines[i].points = points

            #print(len(self.pikets))
            #print(len(self.pikets_labels))
            #print(len(self.pikets))
            #print(len(self.pikets_labels))

            for i in range(len(self.pikets)):
                piket_pos = list(self.pikets[i].pos)
                piket_pos[0] *= self.scale
                piket_pos[1] *= self.scale
                self.pikets[i].pos = piket_pos
                label_pos = list(self.pikets_labels[i].pos)
                label_pos[0] = piket_pos[0]-25
                label_pos[1] = piket_pos[1]-25
                self.pikets_labels[i].pos = label_pos
            
            for i in range(len(self.selected_pikets)):
                piket_pos = list(self.selected_pikets[i].pos)
                piket_pos[0] *= self.scale
                piket_pos[1] *= self.scale
                self.selected_pikets[i].pos = piket_pos
                label_pos = list(self.selected_pikets_labels[i].pos)
                label_pos[0] = piket_pos[0]-25
                label_pos[1] = piket_pos[1]-25
                self.selected_pikets_labels[i].pos = label_pos

            self.moving_touches = []

        #self.line.points = 
        #return super().on_touch_move(touch)
    def on_touch_up(self, touch):
        self.moving_touches = []



class Piket_name_setting(BoxLayout):
    piket_name = StringProperty()
    def __init__(self,piket_name,**kwargs):
        super(Piket_name_setting,self).__init__(**kwargs)
        '''self.text_input = TextInput(text='Hello world')
        self.button_accept = Button(text = "Ok")
        self.button_accept.bind(on_press = self.save_piket_name)
        self.add_widget(self.text_input)
        self.add_widget(self.button_accept)'''
        self.text_input = TextInput(text=str(piket_name))
        self.button_accept = Button(text='Ok')
        self.button_accept.bind(on_press=self.save_piket_name)
        #self.text_input.bind()
        self.add_widget(self.text_input)
        self.add_widget(self.button_accept)

    def say_im_alive(self,instance):
        print("i am alive")
    
    def save_piket_name(self,instance):
        print("я задаю имя пикетв")
        self.piket_name = self.text_input.text
    
    def destroy(self):
        #self.remove_widget(self.button_accept)
        #self.remove_widget(self.text_input)
        self.parent.remove_widget(self)

#bind не заменяет функция а добавляет их
class Map_screen(FloatLayout):
    def __init__(self,map_name,**kwargs):
        super(Map_screen,self).__init__(**kwargs)
        
        self.map_name = map_name
        
        self.menu = Menu_Widget(orientation = "vertical",pos = [0,0],  size_hint = [.2,.3])
        self.map_canvas = PainterWidget()
        #self.scatter=Scatter(do_rotation=False, do_translation = False)
        #self.fl.map_canvas.bind(moving_offsets = self.move_piket_window)
        #self.canvas_modes = dict(zip(self.menu.mode_list,[self.set_canvas_mode_free,self.set_canvas_mode_pikets,self.set_canvas_mode_drawing]))
        self.menu.bind(scale = self.change_scale)
        self.menu.bind(mode = self.change_mode)
        
        self.map_canvas.bind(new_piket_pos = self.make_piket_setting_window)
        self.map_canvas.bind(view_point_coords = self.update_view_point)
        #self.map_canvas.bind(offsets = self.move_piket_window)
        
        self.exit_button = Button(text = "X",size_hint = [0.05,0.05],pos = [0,Window.size[1]*0.95])
        self.exit_button.bind(on_press = self.open_map_list)
        self.add_widget(self.menu,index=0)
        self.add_widget(self.map_canvas,index=1)
        self.add_widget(self.exit_button,index = 0)
        self.view_point_coords = self.map_canvas.view_point_coords
        self.piket_window = False
        self.upload_map_from_file()
        self.data_receive_process = Clock.schedule_interval(self.get_vec_from_device, 0.1)
        self.data_saving_process = Clock.schedule_interval(self.save_map_data, 1)
        

    def open_map_list(self,instance):
        self.data_receive_process.cancel()
        self.data_saving_process.cancel()
        self.parent.change_screen(Menu_screen())

    def upload_map_from_file(self):
        file_path = f"maps/{self.map_name}.json"
        with open(file_path, 'r', encoding='utf-8') as fh: #открываем файл на чтение
            data = json.load(fh) #загружаем из файла данные в словарь data
        with self.map_canvas.canvas:
            for line_points in data["lines"]:
                Color(0,1,0,1)
                self.map_canvas.lines.append(Line(points = line_points))
            for i in range(len(data["pikets"])):
                Color(0,0,1,1)
                self.map_canvas.pikets.append(Ellipse(pos = data["pikets"][i],size = (8,8),index = 1))
                self.map_canvas.pikets_labels.append(Label(text = data["labels"][i],pos = [data["pikets"][i][0]-25,data["pikets"][i][1]-25],color = (0,0,1,1),halign = "left"))

        print(data)

    def save_map_data(self,dt):
        lines = self.map_canvas.lines + self.map_canvas.selected_lines
        pikets = self.map_canvas.pikets+self.map_canvas.selected_pikets
        labels = self.map_canvas.pikets_labels +self.map_canvas.selected_pikets_labels
        lines_points = []
        pikets_points = []
        labels_text = []

        for line in lines:
            lines_points.append([(line.points[0]-self.map_canvas.total_offset_x)/self.map_canvas.scale,(line.points[1]-self.map_canvas.total_offset_y)/self.map_canvas.scale,(line.points[2]-self.map_canvas.total_offset_x)/self.map_canvas.scale,(line.points[3]-self.map_canvas.total_offset_y)/self.map_canvas.scale])
        for piket in pikets:
            pikets_points.append([(piket.pos[0]-self.map_canvas.total_offset_x)/self.map_canvas.scale,(piket.pos[1]-self.map_canvas.total_offset_y)/self.map_canvas.scale])
        for label in labels:
            labels_text.append(label.text)

        data = {"lines":lines_points,"pikets":pikets_points,"labels":labels_text}
        with open(f'maps/{self.map_name}.json', 'w') as fp:
            json.dump(data, fp)
        print("saved")

    def get_vec_from_device(self, dt):
        #print(socket.gethostbyname(socket.gethostname()))

        if socket.gethostbyname(socket.gethostname()) == "192.168.4.2":
            url_vec = "http://192.168.4.1/get_vector"
            response = requests.get(url_vec)
            # Print the response from the ESP32
            #print(response.status_code)
            #print(response.text)
            print(response.status_code)
            if response.status_code == 200:
                coords = list(map(float,response.text.split(",")[:-1]))
                target_point_vec = coords
                print(target_point_vec)
                self.map_canvas.make_survey(target_point_vec)
                #self.map_canvas.canvas.remove(self.map_canvas.direction_line)
                #print(response)
            elif response.status_code == 204:
            
                if self.map_canvas.direction_line_exist:
                    if self.map_canvas.mode =="view_point":
                        self.map_canvas.view_point.pos =  self.map_canvas.survey_point.pos
                    
                    #добавить координаты точки
                    self.map_canvas.new_line_points =  []
                    self.map_canvas.canvas.remove(self.map_canvas.direction_line)
                    self.map_canvas.canvas.remove(self.map_canvas.survey_point)
                    self.new_line_points = []     
                    self.map_canvas.direction_line_exist = False
            
        #print(f"view point {self.view_point_coords}")
    #def move_piket_window(self,instance,offsets):
        #if self.piket_window !=False:
            
            #self.piket_window.pos = (self.piket_window.pos[0]+offsets[0],self.piket_window.pos[1]+offsets[1])
            #self.map_canvas.new_piket.pos = [self.map_canvas.new_piket.pos[0]+offsets[0],self.map_canvas.new_piket.pos[1]+offsets[1]]
    def update_view_point(self,instance,view_point_coords):
        self.view_point_coords = view_point_coords

    def change_mode(self,instance,mode):
        self.map_canvas.mode = mode
        #self.remove_widget(self.menu)#удалить
    def change_scale(self,instance,scale):
        #new_scale = self.map_canvas.scale + scale_bias[1]

        self.map_canvas.scale =1/self.map_canvas.scale
        self.map_canvas.change_scale()
        self.map_canvas.scale = scale
        print(f"new_scale = {scale}")
        #self.menu.scale_bias = 
        self.map_canvas.change_scale()
    def make_piket_setting_window(self,instance,piket_pos):
        if self.piket_window == False:
            #self.fl.map_canvas.pikets.append(self.fl.map_canvas.new_piket)
            #self.add_piket_name(self.fl.piket_window,self.fl.piket_window.text_input.text)
            #self.fl.piket_window = False
            self.piket_window = Piket_name_setting(piket_name=len(self.map_canvas.pikets),pos = (self.size[0]/2,self.size[1]/2),size_hint = [.1,.1])
            self.piket_window.bind(piket_name = self.add_piket_name)
            self.add_widget(self.piket_window,index = 1)
            #self.fl.piket_window = False
        #self.fl.piket_window = False
        

        #self.fl.button = Button(text = "button",pos = piket_pos)
        #self.fl.Button = Button(text = "button",pos = piket_pos)
        #self.fl.Button.bind(on_press = self.del_button)

        #self.fl.add_widget(self.fl.Button,index = 1)
        #print(len(self.pikets_windows))
        
        #self.remove_widget(self.pikets_windows[-1])
        #print(len(self.pikets_windows))
        
        #self.piket_window = Piket_name_setting_test(pos = (200,200) )
        #self.piket_window.bind(piket_name = self.add_piket_name)
        #self.add_widget(self.piket_window,index = 0)
        #self.remove_widget(self.piket_window)
        #self.piket_window = Piket_name_setting_test(pos = piket_pos)
        #self.piket_window.bind(piket_name = self.add_piket_name)

        #self.add_widget (self.piket_window, index=0)
    def add_piket_name(self,instance,piket_name):
        #pass
        print("Я добавляю имя пикета")
        
        instance.destroy()

        self.remove_widget(instance)
        self.map_canvas.add_piket_name(piket_name,instance.pos,instance.size)
        self.piket_window = False
        
        
        
        #
        
    def delete(self):
        for line in self.map_canvas.selected_lines:
            self.map_canvas.canvas.remove(line)
        self.map_canvas.selected_lines = []

        for piket in self.map_canvas.selected_pikets:
            self.map_canvas.canvas.remove(piket)
        self.map_canvas.selected_pikets = []

        for label in self.map_canvas.selected_pikets_labels:
            label.color = (0,0,0,1)
        self.map_canvas.selected_pikets_labels = []


class Map_menu_block(BoxLayout):
    def __init__(self,map_name,**kwargs):
        print(kwargs)
        super(Map_menu_block,self).__init__(**kwargs)
        self.button_open_map = Button(text = map_name,size_hint = [0.80,1])
        self.button_open_map.bind(on_press = self.open_map)
        self.add_widget(self.button_open_map)
        self.add_del_button()

    def add_del_button(self):
        self.button_del =  Button(text = "delete",size_hint = [0.20,1])
        self.button_del.bind(on_press = self.ask_confirmation)
        self.add_widget(self.button_del)

    def add_confirmation(self):
        self.confirm = Button(text = "Yes",size_hint = [0.1,1])
        self.decline = Button(text = "No",size_hint = [0.1,1])
        self.confirm.bind(on_press = self.delete_map)
        self.decline.bind(on_press = self.return_del_button)
        self.add_widget(self.confirm)
        self.add_widget(self.decline)

    def ask_confirmation(self,instance):
        
        self.remove_widget(self.button_del)
        self.add_confirmation()

    def open_map(self,instance):
        self.parent.parent.change_screen(Map_screen(instance.text))

    def delete_map(self,instance):

        os.remove(f"maps/{self.button_open_map.text}.json")
        #self.parent.remove_map_blocks()
        self.parent.update_menu()

    def return_del_button(self,instance):
        self.remove_widget(self.confirm)
        self.remove_widget(self.decline)
        self.add_del_button()




class Menu_screen(FloatLayout):
    def __init__(self,**kwargs):
        super(Menu_screen,self).__init__(**kwargs)
        self.map_list = []
        self.scrolling_touches = []
        last_pos = Window.size[1] - Window.size[1]*0.1
        self.button_add = Button(text = "+",size_hint= [0.2,0.1],pos = [0,last_pos]) 
        self.button_add.bind(on_press = self.open_name_setting)
        self.button_add.pos[1] = Window.size[1]*0.9
        self.add_widget(self.button_add,index = 0)
        for map_name in os.listdir("maps"):
            #self.map_list.append()
            #print(last_pos)
            self.map_list.append(Map_menu_block(map_name.split(".")[0],size_hint= [1,0.1],pos = [0,last_pos-100]))
            last_pos = self.map_list[-1].pos[1]
            #print("button added")
            self.add_widget(self.map_list[-1],index = 1)

    
    def open_name_setting(self,instance):
        self.remove_widget(self.button_add)
        for button in self.map_list:
            self.remove_widget(button)
        self.set_map_name_input = self.text_input = TextInput(text="Новая карта",size_hint= [0.2,0.1],pos = [Window.size[0]/2-Window.size[0]*0.2/2,Window.size[0]/2-Window.size[0]*0.1/2])
        self.btn_create = Button(text = "Ok",size_hint= [0.2,0.1],pos = [Window.size[0]/2-Window.size[0]*0.2/2,Window.size[0]/2-2.7*Window.size[0]*0.1/2])
        self.btn_cancel = Button(text = "Cancel" ,size_hint= [0.2,0.1],pos = [Window.size[0]/2-Window.size[0]*0.2/2,Window.size[0]/2-2.2*Window.size[0]*0.1])
        self.btn_cancel.bind(on_press = self.draw_menu)
        self.btn_create.bind(on_press = self.create_new_map)
        self.add_widget(self.set_map_name_input)
        self.add_widget(self.btn_create)
        self.add_widget(self.btn_cancel)
    
    

    def create_new_map(self,instance):

        if f"{self.set_map_name_input.text}.json" in os.listdir("maps"):
            copy_counter = 0
            while f"{self.set_map_name_input.text}({copy_counter}).json" in os.listdir("maps"):
                copy_counter+=1
            filename = f"{self.set_map_name_input.text}({copy_counter}).json"
        else:
            filename = f"{self.set_map_name_input.text}.json"

        lines_points = []
        pikets_points = []
        labels_text = []

        data = {"lines":lines_points,"pikets":pikets_points,"labels":labels_text}
        with open(f"maps/{filename}", "w+") as fp:
            json.dump(data, fp)
        print("saved")
        self.parent.change_screen(Map_screen(filename.split(".")[0]))
        #self.draw_menu(instance)

    def close_new_map_window(self):
        self.remove_widget(self.btn_create)
        self.remove_widget(self.btn_cancel)
        self.remove_widget(self.set_map_name_input)
    
    def remove_map_blocks(self):
        for map_block in self.map_list:
            self.remove_widget(map_block)
        self.map_list = []

    def draw_menu(self):
        self.map_list = []
        self.scrolling_touches = []
        last_pos = Window.size[1] - 100
        self.button_add = Button(text = "+",size_hint= [0.2,0.1],pos = [0,last_pos]) 
        self.button_add.bind(on_press = self.open_name_setting)
        self.button_add.pos[1] = Window.size[1]*0.9
        self.add_widget(self.button_add,index = 0)
        for map_name in os.listdir("maps"):
            print(last_pos)
            self.map_list.append(Map_menu_block(map_name.split(".")[0],size_hint= [1,0.1],pos = [0,last_pos-100]))
            last_pos = self.map_list[-1].pos[1]
            print("button added")
            self.add_widget(self.map_list[-1],index = 1)
    
    def update_menu(self):
        self.remove_map_blocks()
        self.draw_menu()
    def back_2_menu(self,instance):
        self.close_new_map_window()
        self.draw_menu()
        
    def on_touch_move(self, touch):
        if len(self.scrolling_touches) == 2:
            scrolling_bias = self.scrolling_touches[1]-self.scrolling_touches[0]
            if self.map_list[-1].pos[1]+scrolling_bias > 200:
                scrolling_bias = 200 - self.map_list[-1].pos[1]
            if self.map_list[0].pos[1]+scrolling_bias < Window.size[1] - 200:
                scrolling_bias = Window.size[1] - 200 - self.map_list[0].pos[1]
            print(scrolling_bias)
            #if self.map_list[-1].pos[1] > 20 or scrolling_bias > 0:
            for map_button in self.map_list:
                map_button.pos[1] += scrolling_bias
            self.scrolling_touches =[]
        else:
            self.scrolling_touches.append(touch.y)

    def on_touch_up(self, touch):
        self.scrolling_touches = []
            
        #print(self.map_list)

class Main_container(FloatLayout):
    def __init__(self,**kwargs):
        super(Main_container,self).__init__(**kwargs)
        self.screen = Menu_screen()
        self.add_widget(self.screen)
    
    def change_screen(self,new_screen):
        self.remove_widget(self.screen)
        self.screen = new_screen
        self.add_widget(self.screen)
#self.map_canvas.canvas.add(Color(0,0,1,1))
        #pos = list(self.pos[i] + (self.size[i] - text.size[i]) / 2 for i in range(2))
        #print(piket_name)
        #instance.pos
        #self.canvas.add(Rectangle(size=(20,50), pos=(200,200), text = "hi"))
        #self.map_canvas.piket_labels.append(Rectangle(size=(20,50), pos=(200,200), text = "hi"))
    #self.remove_widget(self.)
class PaintApp(App):
    def build(self):
        #return Map_screen(size_hint = [1,1])#PainterWidget()
        return Main_container(size_hint = [1,1])#PainterWidget()

if __name__ == '__main__':
    PaintApp().run()

