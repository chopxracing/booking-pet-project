
from datetime import datetime

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.db.models import Q, Min, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import DetailView, CreateView
from django.views.generic.list import ListView

from main.models import BookingHistory, BookingFavorites, Hotel, Hotel_Comfort, Hotel_Room, Files, Comfort


# Create your views here.


def home(request):
    return render(request, 'home.html')

def hotels(request):

    data = {
        'hotels': Hotel.objects.all(),
        'hotel_comfort': Hotel_Comfort.objects.all(),
        'min_price': Hotel_Room.objects.order_by('price').first(),
    }

    return render(request, 'hotels.html', data)

def help(request):
    return render(request, 'help.html')

def about(request):
    return render(request, 'about.html')

def loginform(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')

def profile(request):
    # Проверяем, авторизован ли пользователь
    if not request.user.is_authenticated:
        messages.error(request, 'Пожалуйста, войдите в систему')
        return redirect('login')

    # Передаем данные пользователя в шаблон
    context = {
        'user': request.user,
        'bookinghistory': BookingHistory.objects.filter(user_id=request.user.id),
        'active_bookings': BookingHistory.objects.filter(user_id=request.user.id, is_active=True),
        'inactive_bookings': BookingHistory.objects.filter(user_id=request.user.id, is_active=False),
        'bookingfavorites': BookingFavorites.objects.filter(user_id=request.user.id),
    }
    return render(request, 'profile.html', context)

def logincheck(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно вошли')
                return redirect('profile')
            else:
                messages.error('Неверный логин или пароль')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
            return redirect('login')

    return redirect('login')

def createuser(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')

            # Валидация данных
            if not all([first_name, last_name, email, password]):
                messages.error(request, 'Все поля обязательны для заполнения')
                return redirect('register')

            if password != confirm_password:
                messages.error(request, 'Пароли не совпадают')
                return redirect('register')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Пользователь с таким email уже существует')
                return redirect('register')

            # Создаем username из email (убираем @ и домен)
            username = email.split('@')[0]
            # Если username уже существует, добавляем число
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Создаем пользователя
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                date_joined=datetime.now(),
            )

            messages.success(request, 'Аккаунт успешно создан! Теперь вы можете войти.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')
            return redirect('register')

    # Если метод не POST, перенаправляем на регистрацию
    return redirect('register')


class SearchHotel(ListView):
    template_name = 'hotels.html'
    context_object_name = 'hotels'
    paginate_by = 5

    def get_queryset(self):
        queryset = Hotel.objects.all()

        # Получаем все параметры из GET запроса
        name = self.request.GET.get('name')
        city = self.request.GET.get('city')
        stars = self.request.GET.get('stars')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        # Применяем фильтры
        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(city__icontains=city)

        if stars:
            queryset = queryset.filter(stars=stars)
        if min_price:
            # Ищем отели, у которых есть хотя бы один номер с ценой >= min_price
            queryset = queryset.filter(hotel_room__price__gte=min_price).distinct()

        if max_price:
            # Ищем отели, у которых есть хотя бы один номер с ценой <= max_price
            queryset = queryset.filter(hotel_room__price__lte=max_price).distinct()

        # Сортировка
        sort = self.request.GET.get('sort', 'name')
        if sort in ['price_asc', 'price_desc']:
            queryset = queryset.annotate(min_room_price=Min('hotel_room__price'))

        if sort == 'price_asc':
            queryset = queryset.order_by('min_room_price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-min_room_price')
        elif sort == 'stars':
            queryset = queryset.order_by('-stars')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating')
        else:
            queryset = queryset.order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['hotel_comforts'] = Hotel_Comfort.objects.all()
        context['hotel_rooms'] = Hotel_Room.objects.all()
        context['min_price'] = Hotel_Room.objects.order_by('price').first()
        # Сохраняем текущие значения фильтров для формы
        context['current_filters'] = {
            'name': self.request.GET.get('name', ''),
            'city': self.request.GET.get('city', ''),
            'stars': self.request.GET.get('stars', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'sort': self.request.GET.get('sort', 'name'),
        }
        return context


class HotelDetailView(DetailView):
    model = Hotel
    template_name = 'hotel.html'
    context_object_name = 'hotel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hotel = self.get_object()

        context['hotel_comforts'] = Hotel_Comfort.objects.all()
        context['hotel_rooms'] = Hotel_Room.objects.all()
        context['hotel'] = hotel
        context['min_price'] = Hotel_Room.objects.order_by('price').first()
        context['files'] = Files.objects.filter(hotel_id = hotel.id, is_primary=False)

        return context

def clientprofile(request):
    hotels = Hotel.objects.filter(user_id=request.user.id).prefetch_related('hotel_room_set')

    data = {
        'hotels': hotels,
        'hotel_rooms': Hotel_Room.objects.all()
    }
    return render(request, 'clientprofile.html', data)


class HotelRoomsDetailView(DetailView):  # Переименуйте класс, чтобы отразить его назначение, например, HotelDetailView
    model = Hotel  # <--- Фокусируемся на модели Hotel
    template_name = 'rooms.html'
    context_object_name = 'hotel'  # <--- Теперь главный объект в контексте — это отель

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Главный объект теперь - это ОТЕЛЬ (self.get_object() вернет Hotel)
        hotel = self.get_object()

        # Фильтруем все остальные данные, используя этот объект Hotel
        rooms = Hotel_Room.objects.filter(hotel=hotel)

        # Теперь переменная 'hotel' уже есть в контексте
        context['rooms'] = rooms
        context['hotel_comforts'] = Hotel_Comfort.objects.filter(hotel=hotel)
        context['min_price'] = rooms.order_by('price').first()
        context['active_rooms'] = rooms.aggregate(total=Sum('free_count'))['total'] or 0

        return context

class RoomDetailView(DetailView):
    model = Hotel_Room
    template_name = 'room.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        room = self.get_object()
        hotel = room.hotel

        context['hotel'] = hotel
        context['room'] = room
        context['files'] = Files.objects.filter(room_id=room.id, is_primary=False)

        return context


def createroom(request):
    if request.method == 'POST':
        try:
            # 1. Получаем ID отеля и сам объект Hotel
            # ИСПРАВЛЕНО: Теперь ищем по 'hotel_id'
            hotel_id = request.POST.get('hotel_id')

            # Получаем объект Hotel. Если не найден, сразу выдаем 404 (или ошибку)
            hotel_instance = get_object_or_404(Hotel, pk=hotel_id)

            # 2. Получаем остальные данные, преобразуя числа в int/float
            name = request.POST.get('name')
            description = request.POST.get('description')

            # Преобразование в числа для полей IntegerField/DecimalField
            max_people = int(request.POST.get('max_people'))
            price = float(request.POST.get('price'))
            free_count = int(request.POST.get('free_count'))
            rooms = request.POST.get('rooms')

            # 3. ИСПРАВЛЕНО: Убрано 'rooms', которого нет в форме.

            # 4. Создаем объект Hotel_Room
            room = Hotel_Room.objects.create(
                name=name,
                description=description,
                max_people=max_people,
                price=price,
                free_count=free_count,
                rooms=rooms,
                hotel=hotel_instance,
            )

            # 5. Обработка ManyToMany поля (Удобства)
            comfort_ids = request.POST.getlist('comforts')
            if comfort_ids:
                # Находим объекты Comfort по их ID
                comforts_to_add = Comfort.objects.filter(pk__in=comfort_ids)
                # Добавляем их к комнате. Это нужно делать после создания объекта room!
                room.comforts.set(comforts_to_add)

            messages.success(request, 'Номер успешно добавлен!')
            return redirect('rooms', hotel_id)

        except Hotel.DoesNotExist:
            messages.error(request, "Ошибка: Отель не найден.")
            return redirect('rooms', hotel_id)
        except ValueError:
            # Сработает, если max_people, price или free_count не являются корректными числами
            messages.error(request, "Ошибка: Некорректный формат чисел в полях.")
            return redirect('rooms', hotel_id)
        except Exception as e:
            # Логируем ошибку для отладки, но пользователю показываем общее сообщение
            print(f"Произошла необработанная ошибка: {e}")
            messages.error(request, "Произошла непредвиденная ошибка при добавлении номера.")
            return redirect('rooms', hotel_id)

def createhotel(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            city = request.POST.get('city')
            stars = request.POST.get('stars')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            location = request.POST.get('location')
            about = request.POST.get('about')
            to_center = request.POST.get('to_center')


            hotel = Hotel.objects.create(
                name=name,
                city=city,
                stars=stars,
                location=location,
                phone=phone,
                email=email,
                about=about,
                to_center=to_center,
                status_id=1,
                user_id=request.user.id,
            )
            messages.success(request, "Отправлено на проверку")
            return redirect('client')

        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')
            return redirect('client')


def uploadhotelphoto(request):
    if request.method == 'POST':

        try:
            uploaded_file = request.FILES.get('image')
            hotel_id = request.POST.get('hotel_id')
            is_primary = request.POST.get('is_primary') == 'on'
            description = request.POST.get('description')

            if not uploaded_file:
                messages.error(request, 'Файл для загрузки не найден.')
                return redirect('client')


            # Проверка, что отель существует и принадлежит пользователю
            hotel = get_object_or_404(Hotel, id=hotel_id)

            # 4. Если нужно сделать фото основным, сбросить старое основное фото
            if is_primary:
                Files.objects.filter(hotel=hotel, is_primary=True).update(is_primary=False)



            files = Files.objects.create(
                file=uploaded_file,
                hotel=hotel,
                room=None,
                user=request.user,
                description=description,
                is_primary=is_primary
            )

            messages.success(request, f'Фото "{uploaded_file.name}" успешно загружено к отелю "{hotel.name}".')
            return redirect('client')

        except Hotel.DoesNotExist:
            messages.error(request, 'Выбранный отель не существует.')
            return redirect('client')
        except Exception as e:
            # Теперь ловим менее общие ошибки, но оставляем общий Exception на всякий случай
            messages.error(request, f'Произошла критическая ошибка при загрузке фото: {e}')
            return redirect('client')

    # Если метод не POST, просто перенаправляем обратно
    return redirect('client')


class BookRoomDetailView(DetailView):
    model = Hotel_Room
    template_name = 'bookroom.html'
    context_object_name = 'bookroom'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        room = self.get_object()
        hotel = room.hotel

        context['hotel'] = hotel
        context['room'] = room
        context['files'] = Files.objects.filter(room_id=room.id, is_primary=False)

        return context


def uploadroomphoto(request, pk):
    if request.method == 'POST':
        try:
            uploaded_files = request.FILES.getlist('photos')  # Изменено на getlist
            hotel_id = request.POST.get('hotel_id')
            room_id = request.POST.get('room_id')
            description = request.POST.get('description')
            primary_photo_index = request.POST.get('primary_photo_index', 0)

            if not uploaded_files:
                messages.error(request, 'Файлы для загрузки не найдены.')
                return redirect('room_detail', pk=room_id)

            # Проверка, что отель и комната существуют и принадлежат пользователю
            hotel = get_object_or_404(Hotel, id=hotel_id)
            room = get_object_or_404(Hotel_Room, id=room_id, hotel__user=request.user)

            # Обрабатываем каждое загруженное фото
            for index, uploaded_file in enumerate(uploaded_files):
                is_primary = (int(primary_photo_index) == index)

                # Если нужно сделать фото основным, сбросить старое основное фото для этой комнаты
                if is_primary:
                    Files.objects.filter(room=room, is_primary=True).update(is_primary=False)

                files = Files.objects.create(
                    file=uploaded_file,
                    hotel=hotel,
                    room=room,
                    user=request.user,
                    description=description,
                    is_primary=is_primary
                )

            messages.success(request, f'{len(uploaded_files)} фото успешно загружено для номера "{room.name}".')
            return redirect('room_detail', pk=room_id)

        except Hotel.DoesNotExist:
            messages.error(request, 'Выбранный отель не существует.')
            return redirect('room_detail', pk=room_id)
        except Hotel_Room.DoesNotExist:
            messages.error(request, 'Выбранный номер не существует или у вас нет к нему доступа.')
            return redirect('room_detail', pk=room_id)
        except Exception as e:
            messages.error(request, f'Произошла ошибка при загрузке фото: {str(e)}')
            return redirect('room_detail', pk=room_id)

    # Если метод не POST, просто перенаправляем обратно
    return redirect('room_detail', pk=pk)