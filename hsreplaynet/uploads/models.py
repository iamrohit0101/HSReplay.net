from enum import IntEnum
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils.timezone import now
from django.core.files.storage import default_storage
from hsreplaynet.utils.fields import IntEnumField, ShortUUIDField


class UploadEventType(IntEnum):
	POWER_LOG = 1
	OUTPUT_TXT = 2
	HSREPLAY_XML = 3

	@property
	def extension(self):
		if self.name == "POWER_LOG":
			return ".power.log"
		elif self.name == "OUTPUT_TXT":
			return ".output.txt"
		elif self.name == "HSREPLAY_XML":
			return ".hsreplay.xml"
		return ".txt"


class UploadEventStatus(IntEnum):
	UNKNOWN = 0
	PROCESSING = 1
	SERVER_ERROR = 2
	PARSING_ERROR = 3
	SUCCESS = 4
	UNSUPPORTED = 5


def _generate_upload_path(instance, filename):
	ts = now()
	extension = UploadEventType(instance.type).extension
	if instance.token_id:
		token = str(instance.token_id)
	else:
		token = "unknown-token"
	yymmdd = ts.strftime("%Y/%m/%d")
	return "uploads/%s/%s/%s%s" % (yymmdd, token, ts.isoformat(), extension)


class UploadEvent(models.Model):
	"""
	Represents a game upload, before the creation of the game itself.

	The metadata captured is what was provided by the uploader.
	The raw logs have not yet been parsed for validity.
	"""
	id = models.BigAutoField(primary_key=True)
	shortid = ShortUUIDField("Short ID")
	token = models.ForeignKey(
		"api.AuthToken", on_delete=models.CASCADE,
		null=True, blank=True, related_name="uploads"
	)
	api_key = models.ForeignKey(
		"api.APIKey", on_delete=models.SET_NULL,
		null=True, blank=True, related_name="uploads"
	)
	type = IntEnumField(enum=UploadEventType)
	game = models.ForeignKey(
		"games.GameReplay", on_delete=models.SET_NULL,
		null=True, blank=True, related_name="uploads"
	)
	created = models.DateTimeField(auto_now_add=True)
	upload_ip = models.GenericIPAddressField()
	status = IntEnumField(enum=UploadEventStatus, default=UploadEventStatus.UNKNOWN)
	tainted = models.BooleanField(default=False)
	error = models.TextField(blank=True)
	traceback = models.TextField(blank=True)

	metadata = models.TextField()
	file = models.FileField(upload_to=_generate_upload_path)

	def __str__(self):
		return self.shortid

	@property
	def is_processing(self):
		return self.status in (UploadEventStatus.UNKNOWN, UploadEventStatus.PROCESSING)

	def get_absolute_url(self):
		return reverse("upload_detail", kwargs={"shortid": self.shortid})

	def process(self):
		from hsreplaynet.games.processing import process_upload_event

		process_upload_event(self)


@receiver(models.signals.post_delete, sender=UploadEvent)
def cleanup_uploaded_log_file(sender, instance, **kwargs):
	file = instance.file
	if file.name and default_storage.exists(file.name):
		file.delete(save=False)
