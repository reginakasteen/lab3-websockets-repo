from django.shortcuts import render
from django.db.models import Subquery, OuterRef, Q
from api.models import User, Profile, Task, Message
from api.serializer import UserSerializer, TokenSerializer, RegisterSerializer, TaskSerializer, ProfileSerializer, MessageSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

class TokenView(TokenObtainPairView):
    serializer_class = TokenSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = ([AllowAny])
    serializer_class = RegisterSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    if request.method == "GET":
        context = f"Hello, {request.user}, you're seeing a GET response right now"
        return Response({'response': context}, status=status.HTTP_200_OK)
    elif request.method == "POST":
        text = request.POST.get("text")
        context = f"Hello, {request.user}, your message is: {text}"
        return Response({'response': context}, status=status.HTTP_200_OK)

    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/'
    ]
    return Response(routes)


class TodoListView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        todo = Task.objects.filter(user=user)
        return todo


class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        task_id = self.kwargs['task_id']

        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id, user=user)

        return task

class TodoCompletedView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        task_id = self.kwargs['task_id']

        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id, user=user)

        task.completed = True
        return task
    
class Inbox(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        messages = Message.objects.filter(
            id__in=Subquery(
                User.objects.filter(
                    Q(sender__receiver=user_id) | Q(receiver__sender=user_id)
                ).distinct().annotate(
                    last_message = Subquery(
                        Message.objects.filter(
                            Q(sender=OuterRef('id'), receiver=user_id) | Q(receiver=OuterRef('id'), sender=user_id)
                        ).order_by('-id')[:1].values_list('id', flat=True)
                    )
                ).values_list('last_message', flat=True).order_by('-id')
            )
        ).order_by('-id')

        return messages
    

class GetMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        sender_id = self.kwargs['sender_id']
        receiver_id = self.kwargs['receiver_id']
        
        messages = Message.objects.filter(
            sender__in=[sender_id, receiver_id],
            receiver__in=[sender_id, receiver_id],
        )
        return messages
    
class SendMessage(generics.CreateAPIView):
    serializer_class = MessageSerializer


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    permission_classes = [IsAuthenticated]


class UserSearch(generics.ListAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    #permission_classes = [IsAuthenticated]
    def list(self, req, *args, **kwargs):
        username = self.kwargs['username']
        users = Profile.objects.filter(
            Q(user__username__icontains=username) |
            Q(name__icontains=username) |
            Q(user__email__icontains=username)
        )

        if not users.exists:
            return Response(
                {
                    "detail": "No users found",
                }, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)