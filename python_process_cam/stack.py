import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
from PIL import Image
import numpy as np
import cv2


# basic shader + pyopengl: https://stackoverflow.com/questions/53585040/pyopengl-fragment-shader-texture-sampling 
# output to framebuffer: https://stackoverflow.com/questions/59433403/how-to-save-fragment-shader-image-changes-to-image-output-file




def getFileContent(file):
    content = open(file, 'r').read()
    return content


def main():

    # Initialize glfw
    if not glfw.init():
        return

    # Create window
    window = glfw.create_window(1, 1, "My OpenGL window", None, None)  # Size (1, 1) for show nothing in window
    # window = glfw.create_window(800, 600, "My OpenGL window", None, None)

    # Terminate if any issue
    if not window:
        glfw.terminate()
        return

    # Set context to window
    glfw.make_context_current(window)

    # open camera
    cap = cv2.VideoCapture(1)
    width, height = 1280, 640

    # setup vertices and texcoords
    vertices = [0.0, 0.0,
                 0.0, 1.0,
                 1.0, 1.0,
                 1.0, 0.0]

    texcoords = [0.0, 0.0,
                 0.0, 1.0,
                 1.0, 1.0,
                 1.0, 0.0]

    vertices = np.array(vertices, dtype=np.float32)
    texcoords = np.array(texcoords, dtype=np.float32)

    # Compile shaders
    vertexShader = OpenGL.GL.shaders.compileShader(getFileContent("equirectanguler.vert"), GL_VERTEX_SHADER)
    fragmentShader = OpenGL.GL.shaders.compileShader(getFileContent("equirectanguler.frag"), GL_FRAGMENT_SHADER)
    shader = OpenGL.GL.shaders.compileProgram(vertexShader, fragmentShader)

    # GL stuff
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, vertices)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, texcoords)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)

    # Create render buffer with size (image.width x image.height)
    rb_obj = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rb_obj)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, width, height)

    # Create frame buffer
    fb_obj = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fb_obj)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, rb_obj)

    # Check frame buffer (that simple buffer should not be an issue)
    status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if status != GL_FRAMEBUFFER_COMPLETE:
        print("incomplete framebuffer object")


    # Texture
    texture = glGenTextures(1)
    # Bind texture
    glBindTexture(GL_TEXTURE_2D, texture)
    # Texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)



    glUseProgram(shader)

    # Bind framebuffer and set viewport size
    glBindFramebuffer(GL_FRAMEBUFFER, fb_obj)
    glViewport(0, 0, width, height)

    idx = 1
    while True:

        ret, frame = cap.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        print(frame.shape, 'shape')


        pil_img = Image.fromarray(frame.astype(np.uint8)).convert('RGB')
        pil_img_data = np.fromstring(pil_img.tobytes(), np.uint8)
        
        width = 1280
        height = 720


        glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pil_img_data)


        #


        #

        # Install program
        

        # Draw the quad which covers the entire viewport
        #glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glDrawArrays(GL_QUADS, 0, 4)


        #

        # PNG
        # Read the data and create the image
        
        if True:
            image_buffer = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
            image_out = np.frombuffer(image_buffer, dtype=np.uint8)
            image_out = image_out.reshape(height, width, 4)
            img = Image.fromarray(image_out, 'RGBA')
            img.save(r"res/image_outa%03d.png"%idx)
            idx+=1






    # JPG
    '''
    # Read the data and create the image
    image_buffer = glReadPixels(0, 0, image.width, image.height, GL_RGB, GL_UNSIGNED_BYTE)
    image_out = np.frombuffer(image_buffer, dtype=numpy.uint8)
    image_out = image_out.reshape(image.height, image.width, 3)
    img = Image.fromarray(image_out, 'RGB')
    img.save(r"res/image_out.jpg")
    '''

    #

    # Bind default frame buffer (0)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # Set viewport rectangle to window size
    glViewport(0, 0, 0, 0)  # Size (0, 0) for show nothing in window
    # glViewport(0, 0, 800, 600)

    # Set clear color
    glClearColor(0., 0., 0., 1.)

    #

    # Program loop
    while False:# not glfw.window_should_close(window):
        # Call events
        print('loop')
        glfw.poll_events()

        # Clear window
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw
        #glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glDrawArrays(GL_QUADS, 0, 4)

        # Send to window
        glfw.swap_buffers(window)

        # Force terminate program, since it will work like clicked in 'Close' button
        break

    #

    # Terminate program
    glfw.terminate()


if __name__ == "__main__":
    main()