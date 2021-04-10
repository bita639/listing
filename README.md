# Finder

Rent or Book Room online with Finder

<h2>Live Demo</h2>
[Live Demo](https://mashuk5809.pythonanywhere.com)

<h2>Requirements</h2>
<pre>open requirements.txt file to see requirements</pre>

<h2>Installing</h2>
<pre>open terminal and type</pre>
<code>git clone https://github.com/MahmudulHassan5809/Room-Booking-Finder-Dajngo.git</code><br><br>

<h2>To migrate the database open terminal in project directory and type</h2>
<code>python manage.py makemigrations</code><br>
<code>python manage.py migrate</code>

<h2>Static files collection</h2>
<pre>open terminal and type</pre>
<code>python manage.py collectstatic</code>

<h2>Creating Superuser</h2>
<pre>To create superuser open terminal and type</pre>
<code>python manage.py createsuperuser</code>

<h2>Change In settings.py</h2>
<code>

    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'xxxxxx@gmail.com'
    EMAIL_HOST_PASSWORD = 'xxxxxxxxxx'
    EMAIL_PORT = 587
</code>

<h2> To run the program in local server use the following command </h2>
<code>python manage.py runserver</code>

<p>Then go to http://127.0.0.1:8000 in your browser</p>

<p>
  If You Want To use celery To Auto change the Listing Status Then Uncomment the code in models.py in listings folder.Please Setup Celery and RabbitMQ
<p>

<code>

     #ListingBooking Class
       def save(self, *args, **kwargs):
          create_task = False
          if self.pk is None:
              create_task = True

          super(ListingBooking, self).save(*args, **kwargs)

          if create_task and self.end_time:
              print('okskksksk')
              set_booked_as_inactive.apply_async(
                  args=[self.listing.id, self.id], eta=self.end_time)
</code>


<h2>Author</h2>
<blockquote>
  Mahmudul Hassan<br>
  Email: mahmudul.hassan240@gmail.com
</blockquote>

<div align="center">
    <h3>========Thank You !!!=========</h3>
</div>
