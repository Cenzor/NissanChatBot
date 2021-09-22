from django.contrib import admin
from app.models import TGAccount, SpecialCategory, SpecialItem, Service, TestDrive, FaqList, Car


@admin.register(TGAccount)
class AccountAdmin(admin.ModelAdmin):
	pass


@admin.register(SpecialCategory)
class SpecialCategoryAdmin(admin.ModelAdmin):
	pass


@admin.register(SpecialItem)
class SpecialItemAdmin(admin.ModelAdmin):
	pass


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
	pass


@admin.register(TestDrive)
class TestDriveAdmin(admin.ModelAdmin):
	pass


@admin.register(FaqList)
class FaqListAdmin(admin.ModelAdmin):
	list_display = ('id', 'question', 'short_answer', 'short_keywords')


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
	pass
