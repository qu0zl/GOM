# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ForceEntry'
        db.create_table('gom_forceentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('force', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gom.Force'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gom.Unit'])),
            ('count', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
        ))
        db.send_create_signal('gom', ['ForceEntry'])

        # Adding model 'Force'
        db.create_table('gom_force', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=300, blank=True)),
            ('cost', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('gom', ['Force'])

        # Adding M2M table for field owner on 'Force'
        db.create_table('gom_force_owner', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('force', models.ForeignKey(orm['gom.force'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gom_force_owner', ['force_id', 'user_id'])

        # Adding model 'UnitWeapon'
        db.create_table('gom_unitweapon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('weapon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gom.Weapons'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gom.Unit'])),
            ('nameOverride', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('mountType', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('gom', ['UnitWeapon'])

        # Adding model 'Unit'
        db.create_table('gom_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('shoot', self.gf('django.db.models.fields.SmallIntegerField')(default=3)),
            ('assault', self.gf('django.db.models.fields.SmallIntegerField')(default=3)),
            ('guard', self.gf('django.db.models.fields.SmallIntegerField')(default=12)),
            ('soak', self.gf('django.db.models.fields.SmallIntegerField')(default=12)),
            ('mental', self.gf('django.db.models.fields.SmallIntegerField')(default=7)),
            ('skill', self.gf('django.db.models.fields.SmallIntegerField')(default=3)),
            ('image', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('desc', self.gf('django.db.models.fields.TextField')(max_length=300, blank=True)),
            ('mobility', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('size', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('cost', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('unitType', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('mechaSpecialist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('engineerSpecialist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('medicSpecialist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cmdTek', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('gom', ['Unit'])

        # Adding M2M table for field owner on 'Unit'
        db.create_table('gom_unit_owner', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('unit', models.ForeignKey(orm['gom.unit'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gom_unit_owner', ['unit_id', 'user_id'])

        # Adding M2M table for field perks on 'Unit'
        db.create_table('gom_unit_perks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('unit', models.ForeignKey(orm['gom.unit'], null=False)),
            ('perks', models.ForeignKey(orm['gom.perks'], null=False))
        ))
        db.create_unique('gom_unit_perks', ['unit_id', 'perks_id'])

        # Adding M2M table for field manu on 'Unit'
        db.create_table('gom_unit_manu', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('unit', models.ForeignKey(orm['gom.unit'], null=False)),
            ('manufacturer', models.ForeignKey(orm['gom.manufacturer'], null=False))
        ))
        db.create_unique('gom_unit_manu', ['unit_id', 'manufacturer_id'])

        # Adding M2M table for field modz on 'Unit'
        db.create_table('gom_unit_modz', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('unit', models.ForeignKey(orm['gom.unit'], null=False)),
            ('modz', models.ForeignKey(orm['gom.modz'], null=False))
        ))
        db.create_unique('gom_unit_modz', ['unit_id', 'modz_id'])

        # Adding model 'Weapons'
        db.create_table('gom_weapons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('weaponName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('weaponType', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('weaponRange', self.gf('django.db.models.fields.SmallIntegerField')(default=10)),
            ('weaponDamage', self.gf('django.db.models.fields.SmallIntegerField')(default=10)),
            ('weaponAE', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('weaponAP', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('weaponPoints', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
        ))
        db.send_create_signal('gom', ['Weapons'])

        # Adding model 'Perks'
        db.create_table('gom_perks', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('perkName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('perkDescription', self.gf('django.db.models.fields.CharField')(default='Empty Perk Description', max_length=300)),
            ('perkEffect', self.gf('django.db.models.fields.CharField')(default='Empty Perk Effect', max_length=200)),
            ('perkCost', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
        ))
        db.send_create_signal('gom', ['Perks'])

        # Adding model 'Modz'
        db.create_table('gom_modz', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('perkName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('perkDescription', self.gf('django.db.models.fields.CharField')(default='Empty Perk Description', max_length=300)),
            ('perkEffect', self.gf('django.db.models.fields.CharField')(default='Empty Perk Effect', max_length=200)),
            ('perkCost', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
            ('modzType', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('modzAvailability', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('gom', ['Modz'])

        # Adding model 'Manufacturer'
        db.create_table('gom_manufacturer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manuName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('manuWeb', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('gom', ['Manufacturer'])


    def backwards(self, orm):
        # Deleting model 'ForceEntry'
        db.delete_table('gom_forceentry')

        # Deleting model 'Force'
        db.delete_table('gom_force')

        # Removing M2M table for field owner on 'Force'
        db.delete_table('gom_force_owner')

        # Deleting model 'UnitWeapon'
        db.delete_table('gom_unitweapon')

        # Deleting model 'Unit'
        db.delete_table('gom_unit')

        # Removing M2M table for field owner on 'Unit'
        db.delete_table('gom_unit_owner')

        # Removing M2M table for field perks on 'Unit'
        db.delete_table('gom_unit_perks')

        # Removing M2M table for field manu on 'Unit'
        db.delete_table('gom_unit_manu')

        # Removing M2M table for field modz on 'Unit'
        db.delete_table('gom_unit_modz')

        # Deleting model 'Weapons'
        db.delete_table('gom_weapons')

        # Deleting model 'Perks'
        db.delete_table('gom_perks')

        # Deleting model 'Modz'
        db.delete_table('gom_modz')

        # Deleting model 'Manufacturer'
        db.delete_table('gom_manufacturer')


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
            'shoot': ('django.db.models.fields.SmallIntegerField', [], {'default': '3'}),
            'size': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'skill': ('django.db.models.fields.SmallIntegerField', [], {'default': '3'}),
            'soak': ('django.db.models.fields.SmallIntegerField', [], {'default': '12'}),
            'unitType': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'weapons': ('django.db.models.fields.related.ManyToManyField', [], {'default': '1', 'to': "orm['gom.Weapons']", 'through': "orm['gom.UnitWeapon']", 'symmetrical': 'False'})
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