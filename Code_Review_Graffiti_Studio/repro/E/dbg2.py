from common import *
from photo_prepare import recipe
for kw in [dict(frame=True),dict(frame=False,solid=(40,90,200)),dict(frame=False,solid=(230,200,40),bg=(70,70,75))]:
    im,_=wall_with_panel(**kw);print(kw,recipe(im,'x.jpg')[1])
