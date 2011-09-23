(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('RabbitMQNode', _t('RabbitMQ Node'), _t('RabbitMQ Nodes'));
ZC.registerName('RabbitMQVHost', _t('RabbitMQ VHost'), _t('RabbitMQ VHosts'));
ZC.registerName('RabbitMQExchange', _t('RabbitMQ Exchange'), _t('RabbitMQ Exchanges'));
ZC.registerName('RabbitMQQueue', _t('RabbitMQ Queue'), _t('RabbitMQ Queues'));

Zenoss.types.TYPES.DeviceClass[0] = new RegExp(
    "^/zport/dmd/Devices(/(?!devices)[^/*])*/?$");

Zenoss.types.register({
    'RabbitMQNode':
        "^/zport/dmd/Devices/.*/devices/.*/rabbitmq_nodes/[^/]*/?$",
    'RabbitMQVHost':
        "^/zport/dmd/Devices/.*/devices/.*/rabbitmq_vhosts/[^/]*/?$",
    'RabbitMQExchange':
        "^/zport/dmd/Devices/.*/devices/.*/rabbitmq_exchanges/[^/]*/?$",
    'RabbitMQQueue':
        "^/zport/dmd/Devices/.*/devices/.*/rabbitmq_queues/[^/]*/?$"
});

Ext.apply(Zenoss.render, {
    entityLinkFromGrid: function(obj) {
        if (obj && obj.uid && obj.name) {
            if ( !this.panel || this.panel.subComponentGridPanel) {
                return String.format(
                    '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\'{0}\', \'{1}\');">{1}</a>',
                    obj.uid, obj.name);
            } else {
                return obj.name;
            }
        }
    },

    checkbox: function(bool) {
        if (bool) {
            return '<input type="checkbox" checked="true" disabled="true">';
        } else {
            return '<input type="checkbox" disabled="true">';
        }
    }
});

ZC.RabbitMQComponentGridPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,
    
    jumpToEntity: function(uid, name) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel,
            sm = tree.getSelectionModel(),
            compsNode = tree.getRootNode().findChildBy(function(n){
                return n.text=='Components';
            });
    
        var compType = Zenoss.types.type(uid);
        var componentCard = Ext.getCmp('component_card');
        componentCard.setContext(compsNode.id, compType);
        componentCard.selectByToken(uid);
        sm.suspendEvents();
        compsNode.findChildBy(function(n){return n.id==compType;}).select();
        sm.resumeEvents();
    }
});

ZC.RabbitMQNodePanel = Ext.extend(ZC.RabbitMQComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'RabbitMQNode',
            sortInfo: {
                field: 'queueCount',
                direction: 'DESC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'vhostCount'},
                {name: 'exchangeCount'},
                {name: 'queueCount'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'vhostCount',
                dataIndex: 'vhostCount',
                header: _t('# VHosts'),
                sortable: true,
                width: 80
            },{
                id: 'exchangeCount',
                dataIndex: 'exchangeCount',
                header: _t('# Exchanges'),
                sortable: true,
                width: 80
            },{
                id: 'queueCount',
                dataIndex: 'queueCount',
                header: _t('# Queues'),
                sortable: true,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.RabbitMQNodePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('RabbitMQNodePanel', ZC.RabbitMQNodePanel);

ZC.RabbitMQVHostPanel = Ext.extend(ZC.RabbitMQComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'RabbitMQVHost',
            sortInfo: {
                field: 'queueCount',
                direction: 'DESC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'rabbitmq_node'},
                {name: 'exchangeCount'},
                {name: 'queueCount'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'rabbitmq_node',
                dataIndex: 'rabbitmq_node',
                header: _t('Node'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'exchangeCount',
                dataIndex: 'exchangeCount',
                header: _t('# Exchanges'),
                sortable: true,
                width: 80
            },{
                id: 'queueCount',
                dataIndex: 'queueCount',
                header: _t('# Queues'),
                sortable: true,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.RabbitMQVHostPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('RabbitMQVHostPanel', ZC.RabbitMQVHostPanel);

ZC.RabbitMQExchangePanel = Ext.extend(ZC.RabbitMQComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'RabbitMQExchange',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'rabbitmq_node'},
                {name: 'rabbitmq_vhost'},
                {name: 'exchange_type'},
                {name: 'durable'},
                {name: 'auto_delete'},
                {name: 'arguments'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'rabbitmq_node',
                dataIndex: 'rabbitmq_node',
                header: _t('Node'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'rabbitmq_vhost',
                dataIndex: 'rabbitmq_vhost',
                header: _t('VHost'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 100
            },{
                id: 'exchange_type',
                dataIndex: 'exchange_type',
                header: _t('Type'),
                sortable: true,
                width: 65
            },{
                id: 'durable',
                dataIndex: 'durable',
                header: _t('Durable'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 55
            },{
                id: 'auto_delete',
                dataIndex: 'auto_delete',
                header: _t('Auto-Delete'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'arguments',
                dataIndex: 'arguments',
                header: _t('Arguments'),
                sortable: true,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.RabbitMQExchangePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('RabbitMQExchangePanel', ZC.RabbitMQExchangePanel);

ZC.RabbitMQQueuePanel = Ext.extend(ZC.RabbitMQComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'RabbitMQQueue',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'rabbitmq_node'},
                {name: 'rabbitmq_vhost'},
                {name: 'durable'},
                {name: 'auto_delete'},
                {name: 'arguments'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'rabbitmq_node',
                dataIndex: 'rabbitmq_node',
                header: _t('Node'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'rabbitmq_vhost',
                dataIndex: 'rabbitmq_vhost',
                header: _t('VHost'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 80
            },{
                id: 'durable',
                dataIndex: 'durable',
                header: _t('Durable'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 55
            },{
                id: 'auto_delete',
                dataIndex: 'auto_delete',
                header: _t('Auto-Delete'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'arguments',
                dataIndex: 'arguments',
                header: _t('Arguments'),
                sortable: true,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.RabbitMQQueuePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('RabbitMQQueuePanel', ZC.RabbitMQQueuePanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_rabbitmq_vhosts',
    text: _t('Related VHosts'),
    xtype: 'RabbitMQVHostPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'RabbitMQNode') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.RabbitMQVHostPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_rabbitmq_exchanges',
    text: _t('Related Exchanges'),
    xtype: 'RabbitMQExchangePanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'RabbitMQNode': return true;
            case 'RabbitMQVHost': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.RabbitMQExchangePanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_rabbitmq_queues',
    text: _t('Related Queues'),
    xtype: 'RabbitMQQueuePanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'RabbitMQNode': return true;
            case 'RabbitMQVHost': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.RabbitMQQueuePanel.superclass.setContext.apply(this, [uid]);
    }
}]);

})();
