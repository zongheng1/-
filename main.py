import numpy,scipy,cv2
import sys,os

# 回调函数
def processTitle(InputListInt,arg):
	top=InputListInt[0]
	bottom=InputListInt[1] 
	if(10<(bottom-top)<100):# 字幕的合理的高度应该在10-100
		return top,bottom
	else:
		raise
# 回调函数
def processFrameNumber(InputListInt,arg):
	minutes=InputListInt[0]
	seconds=InputListInt[1] 
	frameNumber=int(minutes*60+seconds)*arg # 允许用户输入的秒数大于60
	if (5<frameNumber<100000):
		return frameNumber
	else:
		raise
# 回调函数
def processNumber(InputListInt,arg):
	if (4<InputListInt[0]<10001):
		return InputListInt[0]
	else:
		raise
# 获取用户输入
def getInput (ask,func,allowEmpty=True,returnDefault=0,arg=0):
	while True:
		try:
			inputStr=input(ask)
			if(inputStr==''):
				if(allowEmpty==True):
					return returnDefault
				else:
					raise
			else:
				inputListStr=inputStr.strip().split(' ')
				InputListInt=list(map(int,inputListStr))
				return func(InputListInt,arg)
		except:
			print ("\n您的输入有误，请重新输入")
# 图片是否不同？
def isDiff (a,b,threshHam):
	def imgToHash(img): #考虑另一种方法，截取左边和中间的两个位置的灰度进行识别
		# 计算等宽比
		scale=int(round(img.shape[1]/img.shape[0]))
		# 取得等宽比缩小图片
		res=cv2.resize(img,(8*scale,8))
		# 将图片转成灰色
		gray=cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
		# 用大津法二值化:自动计算的阈值，返回的数组=函数（源图，手动要求的阈值（0为自动），替换进去的最大值，处理方法）
		ret,thresh = cv2.threshold(gray,0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		# 返回二值化的结果，即哈希结果
		return thresh
	aHash=imgToHash(a)
	bHash=imgToHash(b)
	xorHash=aHash^bHash
	hammingDistance=int(xorHash.sum())
	if(hammingDistance>threshHam):
		return True
	else:
		return False

# 第一步，输入文件，读取到captures

while True:
	try:
		fileName=input(r"请按顺序拉入第一个视频文件，按回车键确认：")
		video=cv2.VideoCapture(fileName)
		captures=[video]
		fps=int(video.get(cv2.CAP_PROP_FPS))
		width=int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
		while True:
			fileName=input(r"请按顺序拉入后续的视频文件，按回车键确认。如果不需要再增加文件，请直接按回车键：")
			if (fileName==''):
				frameQty=int(video.get(cv2.CAP_PROP_FRAME_COUNT))
				break
			else:
				video=cv2.VideoCapture(fileName)
				fpsNew=int(video.get(cv2.CAP_PROP_FPS))
				widthNew=int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
				if (fps==fpsNew and width==widthNew):
					captures.append(video)
				else:
					raise
		break
	except:
		print ("您拉入的视频文件有误，请检查文件完整性，如果您多次拉入文件，请确保它们的宽度高度和帧率是一致的。如果没有以上错误，可能是不支持此视频格式。\n\n\n\n\n请重新开始\n")

#第二步 用户输入需要用到的数值
ask="请输入底部字幕行所在的高度区间。如视频高度360，字幕行出现在高度304和329之间，请输入“304 329”并按回车键确认即可。\n"
subtitleTop,subtitleBottom=getInput(ask,processTitle,False,0)

ask="\n\n\n可选（1/6）\n当镜头切换时，如果需要截取整个画面，请输入视频顶部的标题行的高度区间。如视频高度360，标题行出现在高度30和49之间，请输入“30 49”并按回车键确认即可。\n\n如不需截取请直接按回车键即可\n"
titlePosition=getInput(ask,processTitle,True,0)

ask="\n\n\n可选（2/6）\n请设定开始截取的时间。如1分30秒，请输入“1 30”并按回车键确认。\n\n如果要从视频头部开始，请直接按回车键即可。\n"
frameStart=getInput(ask,processFrameNumber,True,0,fps)

ask="\n\n\n可选（3/6）\n请设定结束截取的时间。如15分15秒，请输入“15 15”并按回车键确认。\n\n如果要截取到视频末尾，请直接按回车键即可。\n"
FrameStop=getInput(ask,processFrameNumber,True,frameQty,fps)

ask="\n\n\n可选（4/6）\n1秒=1000毫秒，最快只需多少毫秒，字幕就会改变？请输入毫秒数，建议范围100-1000，\n\n如果使用默认值500，直接按回车键即可。\n"
ms=getInput(ask,processNumber,True,500)
step=int(round(fps*ms*0.001))

ask="\n\n\n可选（5/6）\n请设定容错度，范围5~1000。容错度高可能导致截取时遗漏不同的字幕/画面，容错度低可能导致重复截取相同字幕/画面。您可以根据实际输出效果，多试几次找出合适的容错度。\n\n如果使用默认值120，请直接按回车键即可。\n"
threshHam=getInput(ask,processNumber,True,120)

ask="\n\n\n可选（6/6）\n请设定输出的字幕文件的高度，建议范围100-10000。\n\n如果使用默认值1000，请直接按回车键即可。（本次按回车键将开始任务！）\n"
tempFileHeight=getInput(ask,processNumber,True,1000)



# 第三步 创建输出目录和初始化输出文件序号
if not (os.path.exists("out")):
	os.mkdir("out")
outDir="out\\1"
i=1
while(os.path.exists(outDir)):
	outDir="out\\{0}".format(i)
	i+=1
os.mkdir(outDir)
tempFileNumber=0

# 第四步 开始处理
videoQty=len(captures)
for index in range(videoQty):
	video=captures[index]
	# 设置frameNow
	if (index==0):
		frameNow=frameStart
		# 在第0次，还要初始化 subtitleOld titleOld temp
		video.set(cv2.CAP_PROP_POS_FRAMES,frameNow)
		success,frame=video.read()
		subtitleOld=frame[subtitleTop:subtitleBottom,0:width]
		if (titlePosition== 0):# 不截取标题行
			temp=subtitleOld
		else: # 截取标题行
			titleTop,titleBottom=titlePosition[0],titlePosition[1]
			titleOld=frame[titleTop:titleBottom,0:width]
			temp=frame
	else:
		frameNow=0
	# 设置FrameEnd
	if (index==videoQty-1):
		FrameEnd=FrameStop
	else:
		FrameEnd=int(video.get(cv2.CAP_PROP_FRAME_COUNT))

		
	# 循环处理一个文件
	while(frameNow<FrameEnd):
		success, frame =video.read()
		subtitle=frame[subtitleTop:subtitleBottom,0:width]
		diff=isDiff(subtitle,subtitleOld,threshHam)
		if(diff):
			if(titlePosition==0):
				temp=numpy.vstack((temp,subtitle))
			else:
				title=frame[titleTop:titleBottom,0:width]
				diff=isDiff(title,titleOld,threshHam)
				if(diff):
					temp=numpy.vstack((temp,frame))
				else:
					temp=numpy.vstack((temp,subtitle))
				titleOld=title
			tempHeight=temp.shape[0]
			if(tempHeight>tempFileHeight):
				cv2.imwrite("{0}\\{1}.jpg".format(outDir,tempFileNumber),temp)
				tempFileNumber+=1
				temp=frame[1:2,0:width] #不知道如何清空temp，所以用这个赋值的方法顶替，顶替后temp内容仅为一行像素，宽度=width
		subtitleOld=subtitle
		frameNow=int(frameNow)+step
		video.set(cv2.CAP_PROP_POS_FRAMES,frameNow)
		sys.stdout.write("\r正在处理第{0}/{1}个视频：已完成:{2}/{3}。已输出{4}个文件到{5}文件夹。".format(index+1,videoQty,frameNow,FrameEnd,tempFileNumber,outDir))

# 循环结束以后，可能由于tempHeight<=tempFileHeight，导致temp的内容没有输出，在此修正
if (tempHeight<=tempFileHeight and temp.shape[0]>2):
	cv2.imwrite("{0}\\{1}.jpg".format(outDir,tempFileNumber),temp)
	tempFileNumber+=1
#结束任务
sys.stdout.write("\r任务已完成。共处理{0}个视频，已输出{1}个文件到{2}文件夹。                            \n".format(videoQty,tempFileNumber,outDir))
input ()
