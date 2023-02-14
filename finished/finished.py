import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import math
import pyrr
import ctypes
from PIL import Image, ImageOps


its_gonna_light = False
once = True

def initialize_glfw():
    glfw.init()
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
    window = glfw.create_window(640, 480, "Title", None, None)
    glfw.make_context_current(window)
    glEnable(GL_PROGRAM_POINT_SIZE)
    glClearColor(0.1, 0.1, 0.1, 1)
    return window
class SimpleComponent:
    def __init__(self, position, eulers):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
class Light:
    def __init__(self, position, color, strength):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength
class Player:
    def __init__(self, position):
        self.position = np.array(position, dtype = np.float32)
        self.theta = 0
        self.phi = 0
        self.update_vectors()
    def update_vectors(self):
        self.forwards = np.array(
            [   np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi))
            ],  dtype = np.float32)
        globalUp = np.array([0,0,1], dtype=np.float32)
        self.up = np.cross(np.cross(self.forwards, globalUp), self.forwards)
class Scene:
    def __init__(self):
        self.cube_position = [6,0,1],
        self.cube_eulers = [270,0,0]

        self.skybox_position = [6, 0, 1],
        self.skybox_eulers = [270, 0, 0]

        self.sun_position = [6, 0, 1],
        self.skybox_eulers = [270, 0, 0]

        self.lights = [
            Light(
                position=[
                    np.random.uniform(low=3.0, high=7.0),
                    np.random.uniform(low=-2.0, high=2.0),
                    np.random.uniform(low=2.0, high=6.0)
                ],
                color=[
                    np.random.uniform(low=0.0, high=0.9),
                    np.random.uniform(low=0.0, high=0.9),
                    np.random.uniform(low=0.0, high=0.9)
                ],
                strength = 4
            )
            for i in range(8)
        ]
        self.player = Player(
            position = [0,0,2]
        )
    def update(self):
        self.cube_eulers[2] += 0.15 * 1.1
        if self.cube_eulers[2] > 360:
            self.cube_eulers[2] -= 360
    def spin_player(self, dTheta, dPhi):
        self.player.theta += dTheta
        if self.player.theta > 360:
            self.player.theta -= 360
        elif self.player.theta < 0:
            self.player.theta += 360
        self.player.phi = min(
            89, max(-89, self.player.phi + dPhi)
        )
        self.player.update_vectors()
class App:
    def __init__(self, window, once):
        self.window = window
        self.renderer = GraphicsEngine()
        self.scene = Scene()
        self.mainLoop(once)
    def mainLoop(self, once):
        running = True
        while (running):
            if glfw.window_should_close(self.window) or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                running = False
            self.handleKeys()
            self.handleMouse()
            glfw.poll_events()
            self.scene.update()
            self.renderer.render(self.scene)
            if its_gonna_light and once:
                self.renderer.destroy()
                once = False
                window = initialize_glfw()
                myApp = App(window, once)
        self.renderer.destroy()
    def handleKeys(self):
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_F) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.player.position += np.array(([0,0,0.15]), dtype = np.float32)
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_G) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.player.position += np.array(([0,0,-0.15]), dtype = np.float32)
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.player.position += np.array(([0.15,0,0]), dtype = np.float32)
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.player.position += np.array(([0,0.15,0]), dtype = np.float32)
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.player.position += np.array(([-0.15,0,0]), dtype = np.float32)
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.player.position += np.array(([0,-0.15,0]), dtype = np.float32)
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_L) == GLFW_CONSTANTS.GLFW_PRESS:
            global its_gonna_light
            its_gonna_light = True
    def handleMouse(self):
        (x,y) = glfw.get_cursor_pos(self.window)
        rate = 0.15
        theta_increment = rate * ((640 / 2) - x)
        phi_increment = rate * ((480 / 2) - y)
        self.scene.spin_player(theta_increment, phi_increment)
        glfw.set_cursor_pos(self.window, 640 / 2, 480 / 2)
class GraphicsEngine:
    def __init__(self):
        self.wood_texture = Material("marble2.jpg")
        self.skybox_texture = Material("universe.jpg")
        self.cube_mesh = Mesh("basic_sphere.obj", 1)
        self.skybox_mesh = Mesh("cube.obj", 3)
        self.sternschnuppe = Material("sternschnuppe.jpg")
        self.light_billboard = BillBoard(w = 0.2, h = 0.2)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glClearColor(0.0, 0.0, 0.0, 1)
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 50, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.lightLocation = {
            "position": [
                glGetUniformLocation(self.shader, f"Lights[{i}].position")
                for i in range(8)
            ],
            "color": [
                glGetUniformLocation(self.shader, f"Lights[{i}].color")
                for i in range(8)
            ],
            "strength": [
                glGetUniformLocation(self.shader, f"Lights[{i}].strength")
                for i in range(8)
            ]
        }
        self.cameraPosLoc = glGetUniformLocation(self.shader, "cameraPostion")
        self.tintLoc = glGetUniformLocation(self.shader, "tint")
    def createShader(self, vertexFilepath, fragmentFilepath):
        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()
        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        return shader
    def render(self, scene):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)
        view_transform = pyrr.matrix44.create_look_at(
            eye = scene.player.position,
            target = scene.player.position + scene.player.forwards,
            up = scene.player.up, dtype = np.float32
        )
        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_FALSE, view_transform)
        glUniform3fv(self.cameraPosLoc, 1, scene.player.position)
        for i,light in enumerate(scene.lights):
            glUniform3fv(self.lightLocation["position"][i], 1, light.position)
            glUniform3fv(self.lightLocation["color"][i], 1, light.color)
            glUniform1f(self.lightLocation["strength"][i], light.strength)
        for i,light in enumerate(scene.lights):
            glUniform3fv(self.tintLoc, 1, light.color)
            directionFromPlayer = light.position - scene.player.position
            angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
            dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
            angle2 = np.arctan2(directionFromPlayer[2],dist2d)
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                model_transform,
                pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32)
            )
            model_transform = pyrr.matrix44.multiply(
                model_transform,
                pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32)
            )
            model_transform = pyrr.matrix44.multiply(
                model_transform,
                pyrr.matrix44.create_from_translation(light.position,dtype=np.float32)
            )
            glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
            glDrawArrays(GL_TRIANGLES, 0, self.light_billboard.vertexCount)
        glUniform3fv(self.tintLoc, 1, np.array([1,1,1], dtype = np.float32))

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(scene.skybox_eulers), dtype=np.float32
            )
        )
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(scene.skybox_position), dtype=np.float32
            )
        )
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)
        self.skybox_texture.use()
        glBindVertexArray(self.skybox_mesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.skybox_mesh.vertex_count)

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(scene.cube_eulers), dtype=np.float32
            )
        )
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(scene.cube_position),dtype=np.float32
            )
        )

        glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,model_transform)
        self.wood_texture.use()
        glBindVertexArray(self.cube_mesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)
        self.sternschnuppe.use()
        glFlush()
    def destroy(self):
        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        self.light_billboard.destroy()
        glDeleteProgram(self.shader)
class Mesh:
    def __init__(self, filename, factor):
        self.vertices = self.loadMesh(filename, factor)
        self.vertex_count = len(self.vertices)//8
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
    def loadMesh(self, filename, factor):
        v = []
        vt = []
        vn = []
        vertices = []
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="v":
                    line = line.replace("  ", " ")
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                elif flag=="vt":
                    line = line.replace("  ", " ")
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag=="vn":
                    line = line.replace("  ", " ")
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag=="f":
                    line = line.replace("  ", " ")
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    line = line.split(" ")

                    faceVertices = []
                    faceTextures = []
                    faceNormals = []

                    if len(line) > 4:
                        line = line[:4]

                    for vertex in line:
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        faceVertices.append(v[position])
                        texture = int(l[1]) - 1
                        if texture < len(vt):
                            faceTextures.append(vt[texture])
                        if len(l) > 2:
                            normal = int(l[2]) - 1
                            faceNormals.append(vn[normal])
                    triangles_in_face = len(line) - 2
                    vertex_order = []
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)

                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                        for x in faceTextures[i]:
                            vertices.append(x)
                        for x in faceNormals[i]:
                            vertices.append(x)
                line = f.readline()
        return vertices
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))
class Material:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        with Image.open(filepath, mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        if its_gonna_light:
            glGenerateMipmap(GL_TEXTURE_2D)
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)
    def destroy(self):
        glDeleteTextures(1, (self.texture,))
class BillBoard:
    def __init__(self, w, h):
        self.vertices = (
            0, -w/2,  h/2, 0, 0, -1, 0, 0,
            0, -w/2, -h/2, 0, 1, -1, 0, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0,
            0, -w/2,  h/2, 0, 0, -1, 0, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0,
            0,  w/2,  h/2, 1, 0, -1, 0, 0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertexCount = 6
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
window = initialize_glfw()
myApp = App(window, True)