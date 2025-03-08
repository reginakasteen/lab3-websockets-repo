from django.db.models import Subquery, OuterRef, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import User, Profile, Task, Message
from api.serializer import UserSerializer, TokenSerializer, RegisterSerializer, TaskSerializer, ProfileSerializer, MessageSerializer


@extend_schema(
    summary="Obtain JWT Token",
    description=(
        "This endpoint allows the user to obtain a JWT token by providing valid user credentials."
        "\nRoute: `/token/` \n\n"
    ),
    request=TokenSerializer,
    responses={200: TokenSerializer, 400: "Bad request (invalid credentials)"},
)
class TokenView(TokenObtainPairView):
    serializer_class = TokenSerializer


@extend_schema(
    summary="New User Registration",
    description=(
        "Creates a new user based on the received data."
        "\nRoute: `/register/` \n\n"
    ),
    request=RegisterSerializer,
    responses={201: RegisterSerializer, 400: "Validation error"},
)
class RegisterView(generics.CreateAPIView):
    """
    Endpoint for registering new users.

    Accepts JSON with user data and creates a new account.
    """
    queryset = User.objects.all()
    permission_classes = ([AllowAny])
    serializer_class = RegisterSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_online(request):
    profile = Profile.objects.get(user=request.user)
    profile.is_online = True
    profile.save()
    return Response({"message": "User is now online"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_offline(request):
    profile = Profile.objects.get(user=request.user)
    profile.is_online = False
    profile.save()
    return Response({"message": "User is now offline"}, status=200)
    

@extend_schema(
    summary="Test View",
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
        Test view

        May contain some useful information in future.

        GET: Return a GET response
        POST: Return a POST response with the text entered earlier

    """
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
    """
        Return a list of available API routes for the application.

        This is a helper view that provides a simple list of the main routes.
    """
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/'
    ]
    return Response(routes)


@extend_schema(
    summary="Retrieve or Create Tasks",
    description=(
        "Retrieve a list of tasks for a specific user or create a new task for the user."
        "\nRoute: `/todo/{user_id}/` \n\n"
    ),
    request=TaskSerializer,
    responses={
        200: TaskSerializer(many=True),
        201: TaskSerializer,
        400: "Bad Request",
        401: "Unauthorized",
        404: "User not found"
    }
)
class TodoListView(generics.ListCreateAPIView):
    """
        Endpoint to retrieve a list of tasks for a specific user or create a new task.

        This endpoint requires a `user_id` parameter in the URL. It retrieves all tasks for the user if using the GET method or creates a new task for the user if using the POST method.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        todo = Task.objects.filter(user=user)
        return todo


@extend_schema(
    summary="Retrieve, Update, or Delete a Task",
    description=(
        "This endpoint allows you to retrieve, update, or delete a task "
        "belonging to a specific user. You must provide both the `user_id` "
        "and `task_id` as URL parameters. Only authenticated users can access this endpoint."
         "\nRoute: `/todo-detail/{user_id}/{task_id}/` \n\n"
    ),
    request=TaskSerializer,
    responses={
        200: TaskSerializer,
        400: "Bad request",
        404: "Not found",
        401: "Unauthorized",
    }
)
class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
   
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        task_id = self.kwargs['task_id']

        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id, user=user)

        return task


@extend_schema(
    summary="Mark Task as Completed",
    description=(
        "Marks the specified task as completed for a specific user."
        "\nRoute: `/todo-completed/{user_id}/{task_id}/` \n\n"
    ),
    request=TaskSerializer,
    responses={
        200: TaskSerializer, 
        404: "Task or user not found", 
        401: "Unauthorized"}
)
class TodoCompletedView(generics.RetrieveUpdateDestroyAPIView):
    """
        Endpoint to mark a task as completed.

        This endpoint requires the `user_id` and `task_id` parameters in the URL. 
        It marks the task as completed for the specified user.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        task_id = self.kwargs['task_id']

        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id, user=user)

        task.completed = True
        return task
    

@extend_schema(
    summary="Retrieve Inbox Messages",
    description=(
        "Retrieves all messages for a specific user, ordered by the most recent."
        "\nRoute: `/todo/{user_id}/` \n\n"
    ),
    request=None,
    responses={
        200: MessageSerializer, 
        401: "Unauthorized", 
        404: "Messages not found"
    }
)
class Inbox(generics.ListAPIView):
    """
        Endpoint to retrieve the inbox messages of a user.

        This endpoint filters messages based on the user's `user_id` and returns them ordered by the most recent.
    """
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
    

@extend_schema(
    summary="Retrieve Messages Between Two Users",
    description=(
        "Retrieves all messages exchanged between two specific users."
        "\nRoute: `/get-messages/{sender_id}/{receiver_id}/` \n\n"
    ),
    request=None,
    responses={
        200: MessageSerializer, 
        401: "Unauthorized", 
        404: "Messages not found"
    }
)
class GetMessagesView(generics.ListAPIView):
    """
        Endpoint to retrieve messages exchanged between two specific users.

        This endpoint requires `sender_id` and `receiver_id` as URL parameters.
    """
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
    

@extend_schema(
    summary="Send a Message",
    description=(
        "Sends a new message from sender to one receiver."
        "\nRoute: `/send-message/` \n\n"
    ),
    request=MessageSerializer,
    responses={
        201: MessageSerializer,
        400: "Bad Request", 
        401: "Unauthorized"
    }
)
class SendMessage(generics.CreateAPIView):
    """
        Endpoint to send a new message between users.

        The user provides message data in the request body, and the message is sent.
    """
    serializer_class = MessageSerializer


@extend_schema(
    summary="Retrieve or Update User Profile",
    description=(
        "Retrieve, update, or delete a user profile. Only the authenticated user can update or delete their own profile."
        "\nRoute: `/profile/{user_id}/` \n\n"
    ),
    request=ProfileSerializer,
    responses={
        200: ProfileSerializer, 
        401: "Unauthorized", 
        404: "Profile not found"
    }
)
class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Endpoint to retrieve, update, or delete a user profile.

        Only authenticated users can update or delete their own profile.
    """
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    permission_classes = [IsAuthenticated]


@extend_schema(
    summary="Search for Users",
    description=(
        "Search for users by username, name, or email." 
        "\nRoute: `search/{username}/` \n\n"
    ),
    request=None,
    responses={
        200: ProfileSerializer, 
        404: "No users found"
        }
)
class UserSearch(generics.ListAPIView):
    """
        Endpoint to search for users by their username, name, or email.

        The search term is passed as a URL parameter `username`.
    """
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    permission_classes = [IsAuthenticated]
    def list(self, req, *args, **kwargs):
        username = self.kwargs['username']
        users = Profile.objects.filter(
            Q(user__username__icontains=username) |
            Q(name__icontains=username) |
            Q(user__email__icontains=username)
        )

        if not users.exists():
            return Response(
                {
                    "detail": "No users found"
                }, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    


@extend_schema(
    responses={
        200: ProfileSerializer,
        404: OpenApiResponse(description="Profile not found")
    },
    request=ProfileSerializer,
    description="Endpoint for getting and updating user profile."
)
class UserProfileView(APIView):

    """
    User Profile View

    This endpoint provides access to the current user's profile. 
    Users can retrieve their profile data via GET request and 
    update their profile with a PUT request.

    ## GET Request
    Fetch the current user's profile details.

    ## PUT Request
    Update the current user's profile details. The request body can contain any 
    subset of the profile fields. If the field is not provided, it will not be updated.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get the current user's profile.

        **Response Fields**:
        - `id`: The unique ID of the profile.
        - `name`: The name of the user.
        - `gender`: The gender of the user.
        - `date_of_birth`: The user's birthdate.
        - `bio`: The biography of the user.
        - `photo`: The photo URL of the user.
        - `is_online`: The current online status of the user.

        **Responses**:
        - 200 OK: The user's profile data.
        - 404 Not Found: The profile for the user does not exist.
        """
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found"}, status=404)

    def put(self, request):
        """
        Update the current user's profile.

        The request body can include the following fields:
        - `name`: The name of the user (optional).
        - `gender`: The gender of the user (optional).
        - `date_of_birth`: The birthdate of the user (optional).
        - `bio`: The biography of the user (optional).
        - `photo`: The new photo URL (optional).
        - `is_online`: The online status of the user (optional).

        **Responses**:
        - 200 OK: Successfully updated profile data.
        - 400 Bad Request: The data provided is invalid.
        - 404 Not Found: Profile does not exist.

        **Example Request**:
        ```json
        {
          "name": "New Name",
          "bio": "Updated bio"
        }
        ```

        **Example Response**:
        ```json
        {
          "id": 1,
          "name": "New Name",
          "gender": "Male",
          "date_of_birth": "1990-01-01",
          "bio": "Updated bio",
          "photo": "new-photo-url.jpg",
          "is_online": true
        }
        ```
        """
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found"}, status=404)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    

@extend_schema(
    responses={
        200: ProfileSerializer,
        404: OpenApiResponse(description="Profile not found")
    },
    description="Retrieve the profile of a user by their ID."
)
class ProfileView(generics.RetrieveAPIView):
    """
    Retrieve a Specific User Profile

    This endpoint retrieves a user's profile based on their `user_id`.

    **GET Request**
    Retrieve a user's profile by providing the `user_id` parameter.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve the profile object based on the user ID from the URL.
        
        **Responses**:
        - 200 OK: The user's profile data.
        - 404 Not Found: Profile for the specified user ID does not exist.
        """
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(Profile, user__id=user_id)
    
