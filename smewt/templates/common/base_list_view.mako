<%inherit file="base_style.mako"/>

<div class="container-fluid">

  ${next.body()}

</div>


<%def name="make_title_list(objs)">

  %for i, obj in enumerate(objs):
    %if i % 2 == 0:
      <div class="row-fluid">
    %endif

    <div class="span6">
      ${parent.make_title_box(obj.poster, obj.title, obj.url)}
    </div>

    %if i % 2 == 1:
      </div>
    %endif
  %endfor

  ## close the last line if not done already
  %if len(objs) % 2 == 1:
    </div>
  %endif

</%def>
