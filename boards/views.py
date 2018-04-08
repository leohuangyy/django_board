from django.db.models import Count
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.shortcuts import render,redirect,get_object_or_404
from django.http import Http404
from django.views.generic import UpdateView,ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from .models import Board,Topic,Post
from .forms import NewTopicForm,PostForm



# Create your views here.
def home(request):
	boards = Board.objects.all()
	# boards_names = list()

	# for board in boards:
	# 	boards_names.append(board.name)

	# response_html = '<br>'.join(boards_names)

	# return HttpResponse(response_html)
	return render(request,'home.html',{'boards':boards})

def board_topics(request,pk):
	# try:
	# 	board = Board.objects.get(pk=pk)
	# except Board.DoesNotExist:
	# 	raise Http404
	board = get_object_or_404(Board,pk=pk)
	#topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
	queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
	page = request.GET.get('page',1)

	paginator = Paginator(queryset,20)

	try:
		topics = paginator.page(page)
	except PageNotAnInteger:
		topics = paginator.page(1)
	except EmptyPage:
		topics = paginator.page(paginator.num_pages)

	return render(request,'topics.html',{'board':board,'topics':topics})

@login_required
def new_topic(request,pk):
	board = get_object_or_404(Board,pk=pk)
	if request.method == 'POST':
		form = NewTopicForm(request.POST)
		if form.is_valid():# ask Django to verify the data, check if the form is valid if we can save it in the database: 
			topic = form.save(commit = False)# do not save the data in the database,but only 'in memory'.Return an object hasn't yet been saved to database.
			topic.board = board
			topic.starter = request.user
			topic.save()
			post = Post.objects.create(
				message=form.cleaned_data.get('message'),
				topic=topic,
				created_by=request.user
				)
			return redirect('board_topics',pk=board.pk)
			#return redirect('board_topics',pk=board.pk,topic_pk=topic.pk)#why add topic_pk=topic.pk here?



		# subject = request.POST['subject']
		# message = request.POST['message']
		# topic = Topic.objects.create(
		# 	subject=subject,
		# 	board=board,
		# 	starter =user
		# 	)

		# post = Post.objects.create(
		# 	message=message,
		# 	topic=topic,
		# 	created_by=user
		# 	)
	else:
		form = NewTopicForm()
	return render(request,'new_topic.html',{'board':board,'form':form})



def topic_posts(request,pk,topic_pk):
	topic = get_object_or_404(Topic,board__pk=pk,pk=topic_pk)
	topic.views += 1
	topic.save()
	return render(request,'topic_posts.html',{'topic':topic})

@login_required
def reply_topic(request,pk,topic_pk):
	topic = get_object_or_404(Topic,board__pk=pk,pk=topic_pk)
	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.topic = topic
			post.created_by = request.user
			post.save()

			topic.last_updated = timezone.now()
			topic.save()
			return redirect('topic_posts',pk=pk,topic_pk=topic_pk)
	else:
		form = PostForm()
	return render(request,'reply_topic.html',{'topic':topic,'form':form})

#Generic Class-Based View

@method_decorator(login_required,name='dispatch')
class PostUpdateView(UpdateView):
	model = Post
	fields = ('message',)
	template_name = 'edit_post.html'
	pk_url_kwarg = 'post_pk'
	context_object_name = 'post'

	def get_queryset(self):
		queryset = super().get_queryset()
		return queryset.filter(created_by=self.request.user)

	def form_valid(self,form):
		post = form.save(commit=False)
		post.updated_by = self.request.user
		post.updated_at = timezone.now()
		post.save()
		return redirect('topic_posts',pk=post.topic.board.pk,topic_pk=post.topic.pk)