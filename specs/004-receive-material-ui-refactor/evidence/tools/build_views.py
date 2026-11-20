"""Build spec 004 Receive Material views from the committed baseline (git HEAD).

Usage: python3 -I build_views.py <repo_root>
Writes receiveMaterial/view.json, orderInformation/{view,resource}.json,
operatorInputs/{view,resource}.json. Signatures are stamped separately by igsig.py.
"""
import copy, json, os, subprocess, sys, datetime

REPO = sys.argv[1]
VIEWS = os.path.join(REPO, 'services/ignition/projects/kanoaMES/com.inductiveautomation.perspective/views/training')
RM = os.path.join(VIEWS, 'receiveMaterial')
REL = 'services/ignition/projects/kanoaMES/com.inductiveautomation.perspective/views/training/receiveMaterial/view.json'

base = json.loads(subprocess.check_output(['git', '-C', REPO, 'show', 'HEAD:' + REL]))


def find(node, name):
	if node['meta']['name'] == name:
		return node
	for child in node.get('children', []):
		hit = find(child, name)
		if hit:
			return hit
	return None


def comp(ctype, name, props=None, position=None, propConfig=None, children=None, events=None, meta=None):
	c = {'type': ctype, 'meta': {'name': name}}
	if meta:
		c['meta'].update(meta)
	c['position'] = position or {}
	c['props'] = props or {}
	if propConfig:
		c['propConfig'] = propConfig
	if events:
		c['events'] = events
	if children is not None:
		c['children'] = children
	return c


def prop(path, bidirectional=False, transform=None):
	cfg = {'path': path}
	if bidirectional:
		cfg['bidirectional'] = True
	b = {'binding': {'type': 'property', 'config': cfg, 'overlayOptOut': True}}
	if transform:
		b['binding']['transforms'] = [{'type': 'script', 'code': transform}]
	return b


def expr(expression, transform=None):
	b = {'binding': {'type': 'expr', 'config': {'expression': expression}, 'overlayOptOut': True}}
	if transform:
		b['binding']['transforms'] = [{'type': 'script', 'code': transform}]
	return b


def struct(fields, transform):
	return {'binding': {'type': 'expr-struct', 'config': {'struct': fields, 'waitOnAll': True}, 'overlayOptOut': True,
		'transforms': [{'type': 'script', 'code': transform}]}}


def script(code):
	return {'component': {'onActionPerformed': {'type': 'script', 'scope': 'G', 'config': {'script': code}}}}


LABEL_POS = {'basis': '33.333%', 'shrink': 0}
VALUE_POS = {'basis': '66.667%', 'grow': 1, 'shrink': 1}
ROW_PROPS = {'alignItems': 'center', 'style': {'gap': '5px', 'overflow': 'hidden'}}


def label(name, text, extra_style=None):
	style = {'classes': 'kanoa/font/default', 'textAlign': 'right', 'minWidth': '100px'}
	if extra_style:
		style.update(extra_style)
	return comp('ia.display.label', name, {'text': text, 'style': style}, dict(LABEL_POS))


def row(name, children, basis='30px', props=None, propConfig=None):
	return comp('ia.container.flex', name, copy.deepcopy(props or ROW_PROPS), {'basis': basis, 'shrink': 0},
		propConfig=propConfig, children=children)


EMPTY_DASH = "\tif value is None: return u'\\u2014'\n\tif unicode(value).strip() == '': return u'\\u2014'\n\treturn unicode(value)"


def value_label(name, binding):
	return comp('ia.display.label', name,
		{'style': {'classes': 'kanoa/font/default', 'minWidth': 0, 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'}},
		dict(VALUE_POS), propConfig={'props.text': binding, 'meta.tooltip.text': copy.deepcopy(binding)},
		meta={'tooltip': {'enabled': True}})


# ---------------------------------------------------------------- orderInformation (T003, T012, T013, T021, T025)
old_target = find(base['root'], 'lblTargetValue')['propConfig']['props.text']['binding']
old_sched = find(base['root'], 'lblScheduleValue')['propConfig']['props.text']['binding']

target_binding = copy.deepcopy({'binding': old_target})
target_binding['binding']['config']['struct'] = {'target': '{view.params.order.targetQty}', 'unit': '{view.params.order.unitName}'}
sched_binding = copy.deepcopy({'binding': old_sched})
sched_binding['binding']['config']['path'] = 'view.params.scheduledStart'

col_info = comp('ia.container.flex', 'flxColInfo', {'direction': 'column', 'style': {'gap': '4px', 'minWidth': '320px'}},
	{'basis': '50%', 'grow': 1, 'shrink': 1}, children=[
		row('flxOrderNumber', [label('lblOrderNumberLabel', 'Order #'), value_label('lblOrderNumberValue', prop('view.params.order.orderNumber', transform=EMPTY_DASH))]),
		row('flxTitle', [label('lblTitleLabel', 'Title'), value_label('lblTitleValue', prop('view.params.order.description', transform=EMPTY_DASH))]),
		row('flxTarget', [label('lblTargetLabel', 'Target Qty'), value_label('lblTargetValue', target_binding)]),
		row('flxSchedule', [label('lblScheduleLabel', 'Schedule Date'), value_label('lblScheduleValue', sched_binding)]),
		row('flxStatus', [label('lblStatusLabel', 'Status'), value_label('lblStatusValue', prop('view.params.order.status', transform=EMPTY_DASH))]),
	])

notes_row_props = {'alignItems': 'flex-start', 'style': {'gap': '5px', 'overflow': 'hidden'}}
col_notes = comp('ia.container.flex', 'flxColNotes', {'direction': 'column', 'style': {'gap': '4px', 'minWidth': '320px'}},
	{'basis': '50%', 'grow': 1, 'shrink': 1}, children=[
		row('flxNotes', [
			label('lblNotesLabel', 'Notes', {'paddingTop': '6px'}),
			comp('ia.input.text-area', 'taNotes',
				{'placeholder': 'Add delivery notes', 'style': {'classes': 'kanoa/font/default', 'minWidth': 0, 'resize': 'none', 'overflowY': 'auto'}},
				{'basis': '66.667%', 'grow': 1, 'shrink': 1},
				propConfig={'props.text': prop('view.params.notes', bidirectional=True), 'props.enabled': prop('view.params.enabled')}),
		], basis='68px', props=notes_row_props),
	])

order_info_view = {
	'custom': {},
	'params': {'enabled': True, 'notes': '', 'order': {}, 'scheduledStart': None},
	'propConfig': {
		'params.enabled': {'paramDirection': 'input', 'persistent': True},
		'params.notes': {'paramDirection': 'inout', 'persistent': True},
		'params.order': {'paramDirection': 'input', 'persistent': True},
		'params.scheduledStart': {'paramDirection': 'input', 'persistent': True},
	},
	'props': {'defaultSize': {'height': 180, 'width': 800}},
	'root': comp('ia.container.flex', 'root', {'wrap': 'wrap', 'alignContent': 'flex-start', 'style': {'gap': '6px'}},
		children=[col_info, col_notes]),
}

# ---------------------------------------------------------------- operatorInputs (T004, T016, T017, T026)
def tree(name, data_param, path_param):
	old = copy.deepcopy(find(base['root'], name))
	old['meta'] = {'name': name}
	old['position'] = dict(VALUE_POS)
	old['props']['style'] = {'height': 30, 'minWidth': 0}
	old['propConfig'] = {
		'props.params.values.data': prop('view.params.' + data_param),
		'props.params.values.path': prop('view.params.' + path_param),
	}
	return old


NOT_EMPTY = "\treturn len(value or []) > 0"
IS_EMPTY = "\treturn len(value or []) == 0"
truck_msg = find(base['root'], 'flxCntTruckEmptyMessage')['props']
tank_msg = find(base['root'], 'flxCntTankEmptyMessage')['props']


def empty_row(name, options_param, msg_props):
	return row(name, [
		comp('ia.display.label', name + 'Spacer', {'style': {'minWidth': '100px'}}, dict(LABEL_POS)),
		comp('ia.display.label', name + 'Message', copy.deepcopy(msg_props), {'basis': '66.667%', 'grow': 1, 'shrink': 1}),
	], propConfig={'position.display': prop('view.params.' + options_param, transform=IS_EMPTY)})


operator_inputs_view = {
	'custom': {},
	'params': {'actualQty': None, 'enabled': True, 'qtyEnabled': True, 'tankOptions': [], 'tankPath': None, 'tankTreeData': None,
		'truckOptions': [], 'truckPath': None, 'truckTreeData': None, 'unitName': None, 'unitOptions': []},
	'propConfig': dict(
		[('params.' + k, {'paramDirection': 'input', 'persistent': True}) for k in
			('enabled', 'qtyEnabled', 'tankOptions', 'tankPath', 'tankTreeData', 'truckOptions', 'truckPath', 'truckTreeData', 'unitOptions')] +
		[('params.actualQty', {'paramDirection': 'inout', 'persistent': True}), ('params.unitName', {'paramDirection': 'inout', 'persistent': True})]),
	'props': {'defaultSize': {'height': 110, 'width': 800}},
	'root': comp('ia.container.flex', 'root', {'direction': 'column', 'style': {'gap': '4px'}}, children=[
		row('flxTruck', [label('lblTruckLabel', 'Receiving Truck'), tree('evTreeTruck', 'truckTreeData', 'truckPath')],
			propConfig={'position.display': prop('view.params.truckOptions', transform=NOT_EMPTY)}),
		empty_row('flxTruckEmpty', 'truckOptions', truck_msg),
		row('flxTank', [label('lblTankLabel', 'Destination Tank'), tree('evTreeTank', 'tankTreeData', 'tankPath')],
			propConfig={'position.display': prop('view.params.tankOptions', transform=NOT_EMPTY)}),
		empty_row('flxTankEmpty', 'tankOptions', tank_msg),
		row('flxQty', [
			label('lblActualQtyLabel', 'Actual Qty'),
			comp('ia.container.flex', 'flxQtyValue', {'alignItems': 'center', 'style': {'gap': '6px', 'minWidth': 0}},
				{'basis': '66.667%', 'grow': 1, 'shrink': 1}, children=[
					comp('ia.input.numeric-entry-field', 'numActualQty',
						{'format': '#,##0.###', 'spinner': {'enabled': False}, 'style': {'classes': 'kanoa/font/default', 'minWidth': '80px'}},
						{'basis': '80px', 'grow': 1, 'shrink': 1},
						propConfig={'props.value': prop('view.params.actualQty', bidirectional=True), 'props.enabled': prop('view.params.qtyEnabled')}),
					comp('ia.input.dropdown', 'ddUnit',
						{'multiSelect': False, 'showClearIcon': False, 'search': {'enabled': True}, 'style': {'classes': 'kanoa/font/default'}},
						{'basis': '110px', 'shrink': 0},
						propConfig={'props.options': prop('view.params.unitOptions'), 'props.value': prop('view.params.unitName', bidirectional=True),
							'props.enabled': prop('view.params.enabled')}),
				]),
		]),
	]),
}

# ---------------------------------------------------------------- page view (T005–T010, T014, T018, T022, T023, T027)
page = copy.deepcopy(base)
page['props'] = {'defaultSize': {'width': 1200}}

# T006 view state
page['custom'].update({'notesDraft': None, 'unitName': None, 'unitOptions': [], 'warningMessage': '', 'truckTreeData': None, 'tankTreeData': None})
old_truck_data = find(base['root'], 'evTreeTruck')['propConfig']['props.params.values.data']
old_tank_data = find(base['root'], 'evTreeTank')['propConfig']['props.params.values.data']
page['propConfig']['custom.truckTreeData'] = copy.deepcopy(old_truck_data)
page['propConfig']['custom.tankTreeData'] = copy.deepcopy(old_tank_data)
page['propConfig']['custom.warningMessage'] = {'persistent': True, 'onChange': {'enabled': None, 'script':
	"\tmessage = self.custom.warningMessage\n\tif not message:\n\t\treturn\n\tsystem.kanoa.toast.show({'type': 'warning', 'message': message})\n\treturn"}}

# T010 result toast uses order unit
res = page['propConfig']['custom.result']['onChange']['script']
res = res.replace("\ttankName = data.get('tankName') or '-'\n", "\ttankName = data.get('tankName') or '-'\n\tunitText = order.get('unitName') or 'kg'\n")
res = res.replace("'Receipt complete for order %s: lot %s, %s kg, truck %s, tank %s.' % (orderNumber, lotName, quantityText, truckName, tankName)",
	"'Receipt complete for order %s: lot %s, %s %s, truck %s, tank %s.' % (orderNumber, lotName, quantityText, unitText, truckName, tankName)")
res = res.replace("'Receipt recorded for order %s: lot %s (%s kg) remains at truck %s. Open Pending Transfers to complete the move to tank %s.' % (orderNumber, lotName, quantityText, truckName, tankName)",
	"'Receipt recorded for order %s: lot %s (%s %s) remains at truck %s. Open Pending Transfers to complete the move to tank %s.' % (orderNumber, lotName, quantityText, unitText, truckName, tankName)")
assert res.count('unitText') == 3, 'result script anchors changed'
page['propConfig']['custom.result']['onChange']['script'] = res

# T007 startup additions
start = page['events']['system']['onStartup']['config']['script']
start = start.replace("\tself.custom.errorMessage = ''\n", "\tself.custom.errorMessage = ''\n\tself.custom.warningMessage = ''\n", 1)
anchor = "\t\tassetsResult = kanoaScripts.custom.ops.receiving.getReceivingAssets()\n"
assert start.count(anchor) == 1
units_block = (
	"\t\tself.custom.notesDraft = self.custom.orderNotes or ''\n"
	"\t\torderUnit = (self.custom.order or {}).get('unitName')\n"
	"\t\tself.custom.unitName = orderUnit\n"
	"\t\tif not orderUnit and (self.custom.order or {}).get('workOrderId') is not None:\n"
	"\t\t\tself.custom.errorMessage = 'This order has no unit of measure. Ask a supervisor to correct the order.'\n"
	"\t\tunitOptions = []\n"
	"\t\ttry:\n"
	"\t\t\tunitRows = system.kanoa.utilities.convertDatasetToJSON(system.kanoa.item.getItemUnits({'enabled': True}))\n"
	"\t\t\tunitOptions = [{'label': row.get('itemUnitName'), 'value': row.get('itemUnitName')} for row in unitRows if row.get('itemUnitName')]\n"
	"\t\texcept Exception as unitsExc:\n"
	"\t\t\tkanoaScripts.custom.ops.receiving.getLogger().warn('Receive Material unit list load failed: %s' % str(unitsExc))\n"
	"\t\tif orderUnit and orderUnit not in [option['value'] for option in unitOptions]:\n"
	"\t\t\tunitOptions.insert(0, {'label': orderUnit, 'value': orderUnit})\n"
	"\t\tself.custom.unitOptions = unitOptions\n"
)
start = start.replace(anchor, units_block + anchor)
page['events']['system']['onStartup']['config']['script'] = start

# T023 notes save in confirm handler
handlers = page['root']['scripts']['messageHandlers']
confirm = [h for h in handlers if h['messageType'] == 'confirmReceiveOrder'][0]
anchor = "\t\t\tself.view.custom.result = result\n"
assert confirm['script'].count(anchor) == 1
notes_block = (
	"\t\t\tself.view.custom.result = result\n"
	"\t\t\tif result.get('status') in ('SUCCESS', 'TRANSFER_PENDING'):\n"
	"\t\t\t\tnotesDraft = self.view.custom.notesDraft or ''\n"
	"\t\t\t\tif notesDraft != (self.view.custom.orderNotes or ''):\n"
	"\t\t\t\t\tlogger = kanoaScripts.custom.ops.receiving.getLogger()\n"
	"\t\t\t\t\tlogger.info('Receive notes save start workOrderId=%s' % workOrderId)\n"
	"\t\t\t\t\ttry:\n"
	"\t\t\t\t\t\tuserId = system.kanoa.security.getIDPUserId(self.session.props.auth.user)\n"
	"\t\t\t\t\t\tsystem.kanoa.order.updateProductionOrderField(workOrderId, 'note', notesDraft, userId)\n"
	"\t\t\t\t\t\tself.view.custom.orderNotes = notesDraft\n"
	"\t\t\t\t\t\tlogger.info('Receive notes save outcome workOrderId=%s status=SAVED' % workOrderId)\n"
	"\t\t\t\t\texcept Exception as notesExc:\n"
	"\t\t\t\t\t\tlogger.error('Receive notes save failed workOrderId=%s: %s' % (workOrderId, str(notesExc)))\n"
	"\t\t\t\t\t\tself.view.custom.warningMessage = 'Receipt recorded, but the notes were not saved. Re-enter them in the work order editor.'\n"
)
confirm['script'] = confirm['script'].replace(anchor, notes_block)

# Confirm button script (old btnSubmit) with recorded unit in prompt (T009)
old_submit = find(base['root'], 'btnSubmit')['events']['component']['onActionPerformed']['config']['script']
old_msg = "\tmsg = 'Confirm receipt of %s kg for order %s?' % (self.view.custom.actualQtyKg, self.view.custom.order.get('orderNumber') or 'this order')\n"
assert old_submit.count(old_msg) == 1
new_msg = (
	"\tunitOfOrder = self.view.custom.order.get('unitName') or 'kg'\n"
	"\tqtyText = ('{:,.3f}'.format(float(self.view.custom.actualQtyKg))).rstrip('0').rstrip('.')\n"
	"\tmsg = 'Confirm receipt of %s %s for order %s?' % (qtyText, unitOfOrder, self.view.custom.order.get('orderNumber') or 'this order')\n"
)
submit_script = old_submit.replace(old_msg, new_msg)

NOT_DONE = "\tresult = value['result'] or {}\n\tif value['submitting']: return False\n\treturn result.get('status') not in ('SUCCESS', 'TRANSFER_PENDING')"
CONFIRM_ENABLED = ("\tresult = value['result'] or {}\n\tif value['submitting']: return False\n\tif not value['workOrderId']: return False\n"
	"\treturn result.get('status') not in ('SUCCESS', 'TRANSFER_PENDING')")
QTY_ENABLED = find(base['root'], 'numActualQty')['propConfig']['props.enabled']['binding']['transforms'][0]['code']
QTY_ENABLED = QTY_ENABLED.replace("\tif value['submitting']: return False\n",
	"\tif value['submitting']: return False\n\tif (value['result'] or {}).get('status') in ('SUCCESS', 'TRANSFER_PENDING'): return False\n")

ACTION_STYLE = {'classes': 'kanoa/button/flatIcon', 'width': '30px'}
btn_back = comp('ia.input.button', 'btnBack', {'image': {'icon': {'path': 'material/arrow_back'}}, 'style': dict(ACTION_STYLE), 'text': ''},
	{'basis': '30px', 'shrink': 0}, propConfig={'props.enabled': expr('!{view.custom.submitting}')},
	events=script("\tsystem.perspective.navigate(view='training/receivingOrdersSchedule')"),
	meta={'tooltip': {'enabled': True, 'text': 'Back'}})
btn_confirm = comp('ia.input.button', 'btnConfirm', {'image': {'icon': {'path': 'material/check_circle_outline'}}, 'style': dict(ACTION_STYLE), 'text': ''},
	{'basis': '30px', 'shrink': 0},
	propConfig={'props.enabled': struct({'submitting': '{view.custom.submitting}', 'result': '{view.custom.result}', 'workOrderId': '{view.custom.order.workOrderId}'}, CONFIRM_ENABLED)},
	events=script(submit_script), meta={'tooltip': {'enabled': True, 'text': 'Confirm receipt'}})

flx_action = comp('ia.container.flex', 'flxAction', {'alignItems': 'center', 'direction': 'column', 'style': {'gap': '5px', 'padding': '5px'}},
	{'basis': '40px', 'shrink': 0}, children=[btn_back, btn_confirm])
flx_actions = comp('ia.container.flex', 'flxActions', {'justify': 'center', 'style': {'classes': 'kanoa/container', 'minWidth': '35px', 'overflow': 'hidden'}},
	{'shrink': 0}, children=[flx_action])

HAS_ORDER = "\treturn bool(value)"
sections_enabled = struct({'submitting': '{view.custom.submitting}', 'result': '{view.custom.result}'}, NOT_DONE)

ev_order = comp('ia.display.view', 'evOrderInformation',
	{'path': 'training/receiveMaterialSections/orderInformation', 'useDefaultHeight': False, 'useDefaultWidth': False,
		'params': {'enabled': True, 'notes': '', 'order': {}, 'scheduledStart': None}, 'style': {'minHeight': '160px'}},
	{'basis': 'auto', 'shrink': 0},
	propConfig={
		'position.display': prop('view.custom.order.workOrderId', transform=HAS_ORDER),
		'props.params.order': prop('view.custom.order'),
		'props.params.scheduledStart': prop('view.custom.scheduledStart'),
		'props.params.notes': prop('view.custom.notesDraft', bidirectional=True),
		'props.params.enabled': copy.deepcopy(sections_enabled),
		'props.style.minHeight': expr("if({page.props.dimensions.viewport.width} < 700, '240px', '160px')"),
	})

ev_inputs = comp('ia.display.view', 'evOperatorInputs',
	{'path': 'training/receiveMaterialSections/operatorInputs', 'useDefaultHeight': False, 'useDefaultWidth': False,
		'params': copy.deepcopy(operator_inputs_view['params']), 'style': {'minHeight': '110px'}},
	{'basis': 'auto', 'shrink': 0},
	propConfig={
		'position.display': prop('view.custom.order.workOrderId', transform=HAS_ORDER),
		'props.params.truckOptions': prop('view.custom.truckOptions'),
		'props.params.tankOptions': prop('view.custom.tankOptions'),
		'props.params.truckTreeData': prop('view.custom.truckTreeData'),
		'props.params.tankTreeData': prop('view.custom.tankTreeData'),
		'props.params.truckPath': prop('view.custom.truckPath'),
		'props.params.tankPath': prop('view.custom.tankPath'),
		'props.params.actualQty': prop('view.custom.actualQtyKg', bidirectional=True),
		'props.params.unitName': prop('view.custom.unitName', bidirectional=True),
		'props.params.unitOptions': prop('view.custom.unitOptions'),
		'props.params.enabled': copy.deepcopy(sections_enabled),
		'props.params.qtyEnabled': struct({'submitting': '{view.custom.submitting}', 'target': '{view.custom.order.targetQty}',
			'received': '{view.custom.receivedQtyKg}', 'result': '{view.custom.result}'}, QTY_ENABLED),
	})

lbl_no_order = copy.deepcopy(find(base['root'], 'lblNoOrder'))
progress = copy.deepcopy(find(base['root'], 'evProgressBar'))
progress['position'] = {'shrink': 0}

flx_content = comp('ia.container.flex', 'flxContent', {'direction': 'column', 'style': {'gap': '6px', 'overflowY': 'auto', 'minWidth': 0, 'padding': '3px'}},
	{'grow': 1, 'shrink': 1, 'basis': '0px'}, children=[lbl_no_order, ev_order, ev_inputs])
flx_main = comp('ia.container.flex', 'flxMain', {'style': {'gap': '3px'}}, {'grow': 1}, children=[flx_actions, flx_content])

new_root = comp('ia.container.flex', 'root', {'direction': 'column', 'style': {'classes': 'kanoa/font/default', 'gap': '2px', 'padding': '3px'}},
	children=[progress, flx_main])
new_root['scripts'] = page['root']['scripts']
page['root'] = new_root


def strip_dom(node):
	node['meta'].pop('domId', None)
	for child in node.get('children', []):
		strip_dom(child)


strip_dom(page['root'])


def write(path, obj):
	if not os.path.isdir(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))
	with open(path, 'w') as f:
		json.dump(obj, f, indent=2, sort_keys=True)


def resource(path):
	now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
	write(path, {'scope': 'G', 'version': 1, 'restricted': False, 'overridable': True, 'files': ['view.json'],
		'attributes': {'lastModification': {'actor': 'admin', 'timestamp': now}, 'lastModificationSignature': ''}})


write(os.path.join(RM, 'view.json'), page)
SECTIONS = os.path.join(VIEWS, 'receiveMaterialSections')
write(os.path.join(SECTIONS, 'orderInformation', 'view.json'), order_info_view)
write(os.path.join(SECTIONS, 'operatorInputs', 'view.json'), operator_inputs_view)
for sub in ('orderInformation', 'operatorInputs'):
	resource(os.path.join(SECTIONS, sub, 'resource.json'))
print('built')
