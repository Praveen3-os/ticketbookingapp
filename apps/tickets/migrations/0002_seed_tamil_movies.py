from django.db import migrations
from datetime import date, time


def seed_tamil_movies(apps, schema_editor):
    Movie = apps.get_model('tickets', 'Movie')
    Theater = apps.get_model('tickets', 'Theater')
    ShowTime = apps.get_model('tickets', 'ShowTime')

    # ── Tamil Movies ────────────────────────────────────────────────────
    movies_data = [
        {
            'title': 'Leo',
            'title_tamil': 'லியோ',
            'description': 'A mild-mannered café owner with a violent past is forced to revisit his old life when his family is threatened. Directed by Lokesh Kanagaraj, this action-thriller features Vijay in a never-before-seen avatar as Parthiban aka Leo Das.',
            'genre': 'action',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'Lokesh Kanagaraj',
            'cast': 'Vijay, Sanjay Dutt, Trisha, Arjun Sarja, Gautham Vasudev Menon',
            'duration_mins': 164,
            'release_date': date(2026, 11, 1),
            'poster_emoji': '🦁',
        },
        {
            'title': 'Jailer',
            'title_tamil': 'ஜெயிலர்',
            'description': 'A retired jailer goes on a rampage after his son, an honest police officer, is framed and killed. Rajinikanth delivers a powerhouse performance in this mass entertainer directed by Nelson Dilipkumar.',
            'genre': 'action',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'Nelson Dilipkumar',
            'cast': 'Rajinikanth, Mohanlal, Jackie Shroff, Shivarajkumar, Ramya Krishnan',
            'duration_mins': 168,
            'release_date': date(2026, 10, 15),
            'poster_emoji': '🔐',
        },
        {
            'title': 'Ponniyin Selvan 3',
            'title_tamil': 'பொன்னியின் செல்வன் 3',
            'description': 'The epic conclusion of Kalki Krishnamurthy\'s legendary novel. The Chola dynasty faces its greatest crisis as Nandini\'s plans reach their climax and Arulmozhivarman must choose between love and duty.',
            'genre': 'drama',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'Mani Ratnam',
            'cast': 'Vikram, Aishwarya Rai, Jayam Ravi, Karthi, Trisha',
            'duration_mins': 172,
            'release_date': date(2026, 11, 10),
            'poster_emoji': '👑',
        },
        {
            'title': 'Vidaamuyarchi',
            'title_tamil': 'விடாமுயற்சி',
            'description': 'A man embarks on a relentless mission to rescue his wife in a foreign land. This edge-of-the-seat thriller stars Ajith Kumar in a gripping survival drama directed by Magizh Thirumeni.',
            'genre': 'thriller',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'Magizh Thirumeni',
            'cast': 'Ajith Kumar, Trisha, Arjun Das, Regina Cassandra',
            'duration_mins': 145,
            'release_date': date(2026, 11, 5),
            'poster_emoji': '💪',
        },
        {
            'title': 'Amaran',
            'title_tamil': 'அமரன்',
            'description': 'The true story of Major Mukund Varadarajan, a brave Indian Army officer who was posthumously awarded the Ashoka Chakra. A heartfelt patriotic drama that will move you to tears.',
            'genre': 'drama',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'Rajkumar Periasamy',
            'cast': 'Sivakarthikeyan, Sai Pallavi',
            'duration_mins': 158,
            'release_date': date(2026, 10, 31),
            'poster_emoji': '🎖️',
        },
        {
            'title': 'GOAT',
            'title_tamil': 'கோட்',
            'description': 'The Greatest of All Time — A retired special ops agent must come back to save the nation from a new threat, while confronting his own past. Vijay stars in this stylish spy-action blockbuster.',
            'genre': 'action',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'Venkat Prabhu',
            'cast': 'Vijay, Prashanth, Prabhu Deva, Sneha, Laila, Meenakshi Chaudhary',
            'duration_mins': 178,
            'release_date': date(2026, 9, 5),
            'poster_emoji': '🐐',
        },
        {
            'title': 'Kanguva',
            'title_tamil': 'காங்குவா',
            'description': 'A tribal warrior from 1070 AD and a bounty hunter in the present day are connected by a mysterious destiny. This fantasy-action epic spans two timelines in a visual spectacle.',
            'genre': 'sci_fi',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'Siva',
            'cast': 'Suriya, Bobby Deol, Disha Patani',
            'duration_mins': 155,
            'release_date': date(2026, 11, 14),
            'poster_emoji': '⚔️',
        },
        {
            'title': 'Vettaiyan',
            'title_tamil': 'வேட்டையன்',
            'description': 'A fiery encounter specialist questions his own methods when an unexpected turn of events forces him to rethink justice. Rajinikanth stars in this thought-provoking action-drama.',
            'genre': 'action',
            'language': 'tamil',
            'certificate': 'UA',
            'director': 'T.J. Gnanavel',
            'cast': 'Rajinikanth, Amitabh Bachchan, Fahadh Faasil, Rana Daggubati, Manju Warrier',
            'duration_mins': 149,
            'release_date': date(2026, 10, 10),
            'poster_emoji': '🏹',
        },
        {
            'title': 'Demonte Colony 2',
            'title_tamil': 'டிமான்ட் காலனி 2',
            'description': 'The terrifying sequel to the cult Tamil horror hit. A group of friends return to the haunted Demonte Colony, only to discover that the evil has grown far more powerful and personal.',
            'genre': 'horror',
            'language': 'tamil',
            'certificate': 'A',
            'director': 'Ajay Gnanamuthu',
            'cast': 'Arulnithi, Priya Bhavani Shankar',
            'duration_mins': 138,
            'release_date': date(2026, 10, 25),
            'poster_emoji': '👻',
        },
        {
            'title': 'Love Today 2',
            'title_tamil': 'லவ் டுடே 2',
            'description': 'The hilarious sequel where a married couple faces new digital-age relationship challenges. A laugh riot from start to finish with a heartwarming message about trust and love.',
            'genre': 'comedy',
            'language': 'tamil',
            'certificate': 'U',
            'director': 'Pradeep Ranganathan',
            'cast': 'Pradeep Ranganathan, Ivana, Yogi Babu, Sathyaraj',
            'duration_mins': 142,
            'release_date': date(2026, 11, 20),
            'poster_emoji': '❤️',
        },
    ]

    movies = {}
    for md in movies_data:
        m, _ = Movie.objects.get_or_create(title=md['title'], defaults=md)
        movies[md['title']] = m

    # ── Chennai Theaters ────────────────────────────────────────────────
    theaters_data = [
        ('Rohini Silver Screens', 'Koyambedu', 'Chennai', 200),
        ('SPI Sathyam Cinemas', 'Royapettah', 'Chennai', 300),
        ('AGS Cinemas', 'T. Nagar', 'Chennai', 250),
        ('PVR SKLS Galaxy Mall', 'Red Hills', 'Chennai', 180),
        ('INOX National', 'Arcot Road', 'Chennai', 220),
        ('Kamala Cinemas', 'Vadapalani', 'Chennai', 150),
        ('Kasi Theatre', 'Ashok Nagar', 'Chennai', 170),
        ('Vetri Theatre', 'Chromepet', 'Chennai', 160),
        ('Udhayam Theatre', 'Ashok Nagar', 'Chennai', 180),
        ('Devi Theatre Complex', 'Anna Salai', 'Chennai', 200),
    ]

    theaters = []
    for name, loc, city, seats in theaters_data:
        t, _ = Theater.objects.get_or_create(
            name=name, defaults={'location': loc, 'city': city, 'total_seats': seats}
        )
        theaters.append(t)

    # ── Showtimes ── Create shows for next 3 days at top theaters ───────
    from datetime import timedelta
    today = date(2026, 11, 4)
    show_configs = [
        ('morning', time(10, 0), 120.00),
        ('matinee', time(13, 30), 150.00),
        ('first_show', time(16, 30), 150.00),
        ('second_show', time(19, 30), 180.00),
        ('night', time(22, 30), 200.00),
    ]

    for day_offset in range(5):
        show_date = today + timedelta(days=day_offset)
        for movie in list(movies.values())[:6]:  # top 6 movies
            for theater in theaters[:5]:  # top 5 theaters
                for label, st_time, price in show_configs:
                    ShowTime.objects.get_or_create(
                        movie=movie, theater=theater,
                        show_date=show_date, show_label=label,
                        defaults={
                            'show_time': st_time,
                            'price': price,
                            'available_seats': theater.total_seats,
                        }
                    )


def unseed(apps, schema_editor):
    apps.get_model('tickets', 'ShowTime').objects.all().delete()
    apps.get_model('tickets', 'Theater').objects.all().delete()
    apps.get_model('tickets', 'Movie').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [('tickets', '0001_initial')]
    operations = [migrations.RunPython(seed_tamil_movies, unseed)]

