# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Token'
        db.create_table(u'Server_token', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('produce', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'Server', ['Token'])

        # Adding model 'User'
        db.create_table(u'Server_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75, db_index=True)),
            ('age', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('regDate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('lastActivity', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('avatar', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=140, blank=True)),
            ('token', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Server.Token'])),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('gcm_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gcm.Device'], null=True, blank=True)),
            ('count_incoming_messages', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('count_outgoing_messages', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('locale', self.gf('django.db.models.fields.CharField')(default='en', max_length=3)),
            ('device_model', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('app_version', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('user_state', self.gf('django.db.models.fields.CharField')(default='2', max_length=2)),
        ))
        db.send_create_signal(u'Server', ['User'])

        # Adding model 'Message'
        db.create_table(u'Server_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='incoming_message_set', to=orm['Server.User'])),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outgoing_message_set', to=orm['Server.User'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=140, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('preview', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('is_read', self.gf('django.db.models.fields.CharField')(default='0', max_length=1, db_index=True)),
            ('send_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'Server', ['Message'])

        # Adding model 'Error'
        db.create_table(u'Server_error', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('explanation', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('errorid', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Server.User'], null=True, blank=True)),
            ('functionName', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('errorDateTime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'Server', ['Error'])

        # Adding model 'Review'
        db.create_table(u'Server_review', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('valuation', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('review_text', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Server.User'])),
        ))
        db.send_create_signal(u'Server', ['Review'])

        # Adding model 'Feedback'
        db.create_table(u'Server_feedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback_text', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Server.User'])),
        ))
        db.send_create_signal(u'Server', ['Feedback'])


    def backwards(self, orm):
        # Deleting model 'Token'
        db.delete_table(u'Server_token')

        # Deleting model 'User'
        db.delete_table(u'Server_user')

        # Deleting model 'Message'
        db.delete_table(u'Server_message')

        # Deleting model 'Error'
        db.delete_table(u'Server_error')

        # Deleting model 'Review'
        db.delete_table(u'Server_review')

        # Deleting model 'Feedback'
        db.delete_table(u'Server_feedback')


    models = {
        u'Server.error': {
            'Meta': {'object_name': 'Error'},
            'errorDateTime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'errorid': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'functionName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Server.User']", 'null': 'True', 'blank': 'True'})
        },
        u'Server.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'feedback_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Server.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'Server.message': {
            'Meta': {'object_name': 'Message'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_message_set'", 'to': u"orm['Server.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_read': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1', 'db_index': 'True'}),
            'photo': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'preview': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'send_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_message_set'", 'to': u"orm['Server.User']"})
        },
        u'Server.review': {
            'Meta': {'object_name': 'Review'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Server.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'review_text': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'valuation': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'Server.token': {
            'Meta': {'object_name': 'Token'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produce': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'Server.user': {
            'Meta': {'object_name': 'User'},
            'age': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'app_version': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'count_incoming_messages': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'count_outgoing_messages': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'device_model': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'gcm_device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gcm.Device']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastActivity': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'regDate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'token': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Server.Token']"}),
            'user_state': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '2'})
        },
        u'gcm.device': {
            'Meta': {'ordering': "['-modified_date']", 'object_name': 'Device'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dev_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'reg_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['Server']