from django.db import models
from django.contrib import admin
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class LinksToRead(models.Model):
    link = models.URLField()
    title = models.CharField(max_length=125)
    date_added = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __unicode__(self):
        return self.title

### Admin


class PostAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class LinksAdmin(admin.ModelAdmin):
    search_fields = ["title"]


admin.site.register(Post, PostAdmin)
admin.site.register(LinksToRead, LinksAdmin)
