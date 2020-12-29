import cv2
import numpy as np

class GrabCut():
        values = [
	("Definite Background", cv2.GC_BGD,(0,0,0)),
	("Probable Background", cv2.GC_PR_BGD,(0,0,255)),
	("Definite Foreground", cv2.GC_FGD,(255,255,255)),
	("Probable Foreground", cv2.GC_PR_FGD,(255,0,0))
	]
        rectangle=False
        drawing=False
        rect=(0,0,0,0)
        val=2
        thickness=3
        pt=[]
        mode=0
        img=np.zeros((0))
        mask=np.zeros((0))


        def onmouse(self,event,x,y,flags,param):
                if event==cv2.EVENT_RBUTTONDOWN:
                        self.rectangle=True
                        self.pt=[(x,y)]
                elif event==cv2.EVENT_MOUSEMOVE and self.rectangle:
                        img1=self.img.copy()
                        res=cv2.rectangle(img1,self.pt[0],(x,y),(0,255,0),2)
                        cv2.imshow("GrabCut Image",img1)
                elif event==cv2.EVENT_RBUTTONUP and self.rectangle:
                        self.pt.append((x,y))
                        self.rectangle=False
                        self.rect=(self.pt[0][0],self.pt[0][1],self.pt[1][0]-self.pt[0][0],self.pt[1][1]-self.pt[0][1])
                        self.mode=1
                if event==cv2.EVENT_LBUTTONDOWN:
                        if len(self.pt)!=2:
                                print("First of all, draw rectangle...\n")
                        else:
                                self.drawing=True
                                res=cv2.circle(self.img,(x,y),self.thickness,self.values[self.val+1][2],-1)
                                res=cv2.circle(self.mask,(x,y),self.thickness,self.values[self.val][2],-1)
                elif event==cv2.EVENT_MOUSEMOVE and self.drawing:
                        res=cv2.circle(self.img,(x,y),self.thickness,self.values[self.val+1][2],-1)
                        res=cv2.circle(self.mask,(x,y),self.thickness,self.values[self.val][2],-1)
                elif event==cv2.EVENT_LBUTTONUP and self.drawing:
                        self.drawing=False


        def process(self,image_path,output_path):
		image=cv2.imread(image_path)
                self.img=image.copy()
                self.mask=np.zeros(image.shape[:2],dtype="uint8")
                cv2.namedWindow("GrabCut Image")
                cv2.namedWindow("Mask")
                print("Instructions:")
                print("Draw a rectangle around the object using right mouse button (one-time)")
                print("To enhance segmentation, use left mouse button and the following keys")
                print("Key 0: Definite Background")
                print("Key 1: Probable Background")
                print("Key 2: Definite Foreground")
                print("Key 3: Probable Foreground")
                print("To reset everything press r")
                print("To segment image press n")
                print("To save image press s")
                print("To quit press q")
                cv2.setMouseCallback("GrabCut Image",self.onmouse)
                while(True):
                        cv2.imshow("GrabCut Image",self.img)
                        cv2.imshow("Mask",self.mask)
                        key=cv2.waitKey(1) & 0xFF
                        if key==ord('q'):
                                break
                        elif key==ord("0") or key==ord("1"):
                                self.val=0
                        elif key==ord("2") or key==ord("3"):
                                self.val=2
                        elif key==ord("r"):
                                self.mode=0
                                self.img=image.copy()
                                self.mask=np.zeros(image.shape[:2],dtype="uint8")
                                self.rect=(0,0,0,0)
                                self.pt=[]
                                self.rectangle=False
                                self.drawing=False
                                self.val=2
                        elif key==ord("n") or self.mode==1:
                                print("Segmenting...")
                                fgModel=np.zeros((1,65),dtype="float")
                                bgModel=np.zeros((1,65),dtype="float")
                                if self.mode==1:
                                        (self.mask,bgModel,fgModel)=cv2.grabCut(self.img,self.mask,self.rect,bgModel,fgModel,iterCount=1,mode=cv2.GC_INIT_WITH_RECT)
                                        self.mode=0
                                elif self.mode==0:
                                        self.mask[self.mask==0]=cv2.GC_BGD
                                        self.mask[self.mask>0]=cv2.GC_FGD
                                        (self.mask,bgModel,fgModel)=cv2.grabCut(image,self.mask,None,bgModel,fgModel,iterCount=1,mode=cv2.GC_INIT_WITH_MASK)
                                outputMask=np.where((self.mask==cv2.GC_BGD)|(self.mask==cv2.GC_PR_BGD),0,1)
                                outputMask=(outputMask*255).astype("uint8")
                                self.img=cv2.bitwise_and(image,image,mask=outputMask)
                                self.mask=outputMask
                        elif key==ord("s"):
                                output=np.zeros((image.shape[0]*2,image.shape[1],image.shape[2]),dtype="uint8")
                                output[:image.shape[0],:,:]=self.mask
                                output[image.shape[0]:,:,:]=self.img
                                output=cv2.resize(output,image.shape)
                                cv2.imwrite(output_path,output)
                print("Done")

if __name__=='__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("image_path", required=True, help="path to input image")
    ap.add_argument("output_path", required=True, help="path to final image result")
    args = vars(ap.parse_args())
    GrabCut().process(ap.image_path,ap.output_path)