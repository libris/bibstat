define(['jquery', 'amcharts.theme'], function($, AmCharts) {
    var makeChart = function(id, years, chart) {
        var graphs = $.map(years, function(year) {
            return {
                "id": "graph-" + year,
                "title": "År " + year,
                "balloonText": "År " + year + ": [[value]]",
                "valueField": year,
                "fillAlphas": 0.8,
                "lineAlpha": 0.2,
                "type": "column",
                "labelText": "[[value]]"
            }
        });

        AmCharts.makeChart(id, {
            "rotate": true,
            "type": "serial",
            "startDuration": 1,
            "categoryField": "label",
            "categoryAxis": {
                "gridPosition": "start",
                "position": "left"
            },
            numberFormatter: {
                precision: 1,
                decimalSeparator: ',',
                thousandsSeparator: ' '
            },
            "legend": {
                "markerSize": 10,
                "position": "top",
                "useGraphSettings": true
            },
            "graphs": graphs,
            "dataProvider": chart
        });
    };

    return {
        'init': function() {
            $(".chart").each(function() {
                var container = $(this);
                var years = JSON.parse(container.attr('data-years'));
                var chart = JSON.parse(container.attr('data-chart'));

                makeChart(container.attr("id"), years, chart)
            });
        }
    }
});