import media
import fresh_tomatoes

# List of my favourite movies to be generated on the Fresh Tomatoes webpage
films = [
  media.Movie(
    'Deadpool',
    'A former Special Forces operative turned mercenary is subjected to a rogue \
    experiment that leaves him with accelerated healing powers, adopting the \
    alter ego Deadpool.',
    'https://upload.wikimedia.org/wikipedia/en/4/46/Deadpool_poster.jpg',
    'https://www.youtube.com/watch?v=ZIM1HydF9UA'
    ),
  media.Movie(
    'Captain America: Civil War',
    'A feud between Captain America and Iron Man leaves the Avengers in turmoil.',
    'https://upload.wikimedia.org/wikipedia/en/5/53/Captain_America_Civil_War_poster.jpg',
    'https://www.youtube.com/watch?v=xnv__ogkt0M'
    ),
  media.Movie(
    'Batman v Superman',
    'Fearing the actions of Superman are left unchecked, Batman takes on \
    Superman, while the world wrestles with what kind of a hero it really needs.',
    'https://upload.wikimedia.org/wikipedia/en/2/20/Batman_v_Superman_poster.jpg',
    'https://www.youtube.com/watch?v=Cle_rKBpZ28'
    ),
  media.Movie(
    'Gods of Egypt',
    'A common thief joins a mythical god on a quest through Egypt.',
    'https://upload.wikimedia.org/wikipedia/en/2/2f/Gods_of_Egypt_poster.jpg',
    'https://www.youtube.com/watch?v=IJBnK2wNQSo'
    ),
  media.Movie(
    'X-Men: Apocalypse',
    'With the emergence of the world\'s first mutant, Apocalypse, the \
    X-Men must unite to defeat his extinction level plan.',
    'https://upload.wikimedia.org/wikipedia/en/0/04/X-Men_-_Apocalypse.jpg',
    'https://www.youtube.com/watch?v=COvnHv42T-A'
    ),
  media.Movie(
    'Warcraft',
    'An epic fantasy/adventure based on the popular video game series.',
    'https://upload.wikimedia.org/wikipedia/en/5/56/Warcraft_Teaser_Poster.jpg',
    'https://www.youtube.com/watch?v=2Rxoz13Bthc'
    )
  ]

# Generate the Fresh Tomatoes webpage
fresh_tomatoes.open_movies_page(films)