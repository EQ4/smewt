<%inherit file="base_movie.mako"/>

<%!
from smewt.base.utils import tolist, SDict
import datetime

def lastViewedString(m):
    lastViewed = datetime.datetime.fromtimestamp(m.lastViewed).date()
    daysago = (datetime.date.today() - lastViewed).days
    datestr = lastViewed.isoformat()

    if daysago == 0:
        return '<b>Today</b> (%s)' % datestr
    elif daysago == 1:
        return '<b>Yesterday</b> (%s)' % datestr
    elif daysago > 1 and daysago < 8:
        return '<b>%d days ago</b> (%s)' % (daysago, datestr)

    return 'on ' + datestr

%>

<%
movies = sorted([ SDict({ 'title': m.title,
                          'movie': m,
                          'lastViewed': m.lastViewed,
                          'url': '/movie/' + m.title,
                          'poster': m.loresImage })
                  for m in context['movies'] ],
                key = lambda x: -x['lastViewed'])

# keep only the 4 most recent movies
movies = movies[:4]

%>


<%def name="recent_movie_box(m)">
      <div class="well">
        ${parent.make_poster_title(m.poster, m.title, m.url)}

        <p>Last viewed ${lastViewedString(m.movie) | n}</p>

        ${parent.make_movie_comments(m.movie, comment_box_width='98%')}
      </div>
</%def>



<div class="container-fluid">
  <div class="row-fluid">

    ## Left column
    <div class="span6">
      %for m in movies[::2]:
        ${recent_movie_box(m)}
      %endfor
    </div>

    ## Right column
    <div class="span6">
      %for m in movies[1::2]:
        ${recent_movie_box(m)}
      %endfor
    </div>

  </div>
</div>
