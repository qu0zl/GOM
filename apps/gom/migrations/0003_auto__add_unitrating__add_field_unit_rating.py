# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UnitRating'
        db.create_table('gom_unitrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gom.Unit'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('rating', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal('gom', ['UnitRating'])

        # Adding field 'Unit.rating'
        db.add_column('gom_unit', 'rating',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'UnitRating'
        db.delete_table('gom_unitrating')

        # Deleting field 'Unit.rating'
        db.delete_column('gom_unit', 'rating')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gom.force': {
            'Meta': {'object_name': 'Force'},
            'cost': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '300', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'Force Owner Table'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'gom.forceentry': {
            'Meta': {'object_name': 'ForceEntry'},
            'count': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'force': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gom.Force']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gom.Unit']"})
        },
        'gom.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manuName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'manuWeb': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gom.modz': {
            'Meta': {'object_name': 'Modz'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modzAvailability': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'modzType': ('django.db.models.fields.SmallIntegerField', [], {}),
            'perkCost': ('django.db.models.fields.SmallIntegerField', [], {'default': '999'}),
            'perkDescription': ('django.db.models.fields.CharField', [], {'default': "'Empty Perk Description'", 'max_length': '300'}),
            'perkEffect': ('django.db.models.fields.CharField', [], {'default': "'Empty Perk Effect'", 'max_length': '200'}),
            'perkName': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gom.perks': {
            'Meta': {'object_name': 'Perks'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perkCost': ('django.db.models.fields.SmallIntegerField', [], {'default': '999'}),
            'perkDescription': ('django.db.models.fields.CharField', [], {'default': "'Empty Perk Description'", 'max_length': '300'}),
            'perkEffect': ('django.db.models.fields.CharField', [], {'default': "'Empty Perk Effect'", 'max_length': '200'}),
            'perkName': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gom.unit': {
            'Meta': {'object_name': 'Unit'},
            'assault': ('django.db.models.fields.SmallIntegerField', [], {'default': '3'}),
            'cmdTek': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cost': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'creationTime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'max_length': '300', 'blank': 'True'}),
            'engineerSpecialist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'guard': ('django.db.models.fields.SmallIntegerField', [], {'default': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'manu': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'Manu Table'", 'symmetrical': 'False', 'to': "orm['gom.Manufacturer']"}),
            'mechaSpecialist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'medicSpecialist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mental': ('django.db.models.fields.SmallIntegerField', [], {'default': '7'}),
            'mobility': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'modz': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'Modz Table'", 'symmetrical': 'False', 'to': "orm['gom.Modz']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'Owner Table'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'perks': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'Perk Table'", 'blank': 'True', 'symmetrical': 'False', 'to': "orm['gom.Perks']"}),
            'rating': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'shoot': ('django.db.models.fields.SmallIntegerField', [], {'default': '3'}),
            'size': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'skill': ('django.db.models.fields.SmallIntegerField', [], {'default': '3'}),
            'soak': ('django.db.models.fields.SmallIntegerField', [], {'default': '12'}),
            'tempInstance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unitType': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'weapons': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': "orm['gom.Weapons']", 'symmetrical': 'False', 'through': "orm['gom.UnitWeapon']", 'blank': 'True'})
        },
        'gom.unitrating': {
            'Meta': {'object_name': 'UnitRating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gom.Unit']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'gom.unitweapon': {
            'Meta': {'object_name': 'UnitWeapon'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mountType': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'nameOverride': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gom.Unit']"}),
            'weapon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gom.Weapons']"})
        },
        'gom.weapons': {
            'Meta': {'object_name': 'Weapons'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'weaponAE': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'weaponAP': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'weaponDamage': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'weaponName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'weaponPoints': ('django.db.models.fields.SmallIntegerField', [], {'default': '999'}),
            'weaponRange': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'weaponType': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['gom']