(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('RabbitMQNode', _t('RabbitMQ Node'), _t('RabbitMQ Nodes'));
ZC.registerName('RabbitMQVHost', _t('RabbitMQ VHost'), _t('RabbitMQ VHosts'));
ZC.registerName('RabbitMQExchange', _t('RabbitMQ Exchange'), _t('RabbitMQ Exchanges'));
ZC.registerName('RabbitMQQueue', _t('RabbitMQ Queue'), _t('RabbitMQ Queues'));

Ext.apply(Zenoss.render, {
    RabbitMQ_entityLinkFromGrid: function(obj, col, record) {
        if (!obj)
            return;

        if (typeof(obj) == 'string')
            obj = record.data;

        if (!obj.title && obj.name)
            obj.title = obj.name;

        var isLink = false;

        if (this.refName == 'componentgrid') {
            // Zenoss >= 4.2 / ExtJS4
            if (this.subComponentGridPanel || this.componentType != obj.meta_type)
                isLink = true;
        } else {
            // Zenoss < 4.2 / ExtJS3
            if (!this.panel || this.panel.subComponentGridPanel)
                isLink = true;
        }

        if (isLink) {
            return '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\''+obj.uid+'\', \''+obj.meta_type+'\');">'+obj.title+'</a>';
        } else {
            return obj.title;
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

    jumpToEntity: function(uid, meta_type) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel;
        var tree_selection_model = tree.getSelectionModel();
        var components_node = tree.getRootNode().findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.text == 'Components';
                }

                // Zenoss < 4.2 / ExtJS3
                return n.text == 'Components';
            });

        // Reset context of component card.
        var component_card = Ext.getCmp('component_card');

        if (components_node.data) {
            // Zenoss >= 4.2 / ExtJS4
            component_card.setContext(components_node.data.id, meta_type);
        } else {
            // Zenoss < 4.2 / ExtJS3
            component_card.setContext(components_node.id, meta_type);
        }

        // Select chosen row in component grid.
        component_card.selectByToken(uid);

        // Select chosen component type from tree.
        var component_type_node = components_node.findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.id == meta_type;
                }

                // Zenoss < 4.2 / ExtJS3
                return n.id == meta_type;
            });

        if (component_type_node.select) {
            tree_selection_model.suspendEvents();
            component_type_node.select();
            tree_selection_model.resumeEvents();
        } else {
            tree_selection_model.select([component_type_node], false, true);
        }
    }
});

ZC.RabbitMQNodePanel = Ext.extend(ZC.RabbitMQComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'RabbitMQNode',
            sortInfo: {
                field: 'queueCount',
                direction: 'DESC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'vhostCount'},
                {name: 'exchangeCount'},
                {name: 'queueCount'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
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
            autoExpandColumn: 'name',
            componentType: 'RabbitMQVHost',
            sortInfo: {
                field: 'queueCount',
                direction: 'DESC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'rabbitmq_node'},
                {name: 'exchangeCount'},
                {name: 'queueCount'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
                panel: this
            },{
                id: 'rabbitmq_node',
                dataIndex: 'rabbitmq_node',
                header: _t('Node'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
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
            autoExpandColumn: 'name',
            componentType: 'RabbitMQExchange',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'rabbitmq_node'},
                {name: 'rabbitmq_vhost'},
                {name: 'exchange_type'},
                {name: 'durable'},
                {name: 'auto_delete'},
                {name: 'federated'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
                panel: this
            },{
                id: 'rabbitmq_node',
                dataIndex: 'rabbitmq_node',
                header: _t('Node'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
                width: 140
            },{
                id: 'rabbitmq_vhost',
                dataIndex: 'rabbitmq_vhost',
                header: _t('VHost'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
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
                id: 'federated',
                dataIndex: 'federated',
                header: _t('Federated'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
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
            autoExpandColumn: 'name',
            componentType: 'RabbitMQQueue',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'rabbitmq_node'},
                {name: 'rabbitmq_vhost'},
                {name: 'durable'},
                {name: 'auto_delete'},
                {name: 'federated'},
                {name: 'threshold_messages_max'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
                panel: this
            },{
                id: 'rabbitmq_node',
                dataIndex: 'rabbitmq_node',
                header: _t('Node'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
                width: 140
            },{
                id: 'rabbitmq_vhost',
                dataIndex: 'rabbitmq_vhost',
                header: _t('VHost'),
                renderer: Zenoss.render.RabbitMQ_entityLinkFromGrid,
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
                id: 'federated',
                dataIndex: 'federated',
                header: _t('Federated'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'threshold_messages_max',
                dataIndex: 'threshold_messages_max',
                header: _t('Threshold'),
                sortable: true,
                width: 70
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
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
