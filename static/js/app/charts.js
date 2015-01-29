define(['jquery', 'amcharts.theme'], function ($, AmCharts) {
    var makeChart = function (id, years, chart) {
        var colors = {};
        colors[years[0]] = "#f29400";
        colors[years[1]] = "#b9cb00";
        colors[years[2]] = "#98a338";

        var graphs = years.map(function (year) {
            return {
                "id": "graph-" + year,
                "title": "År " + year,
                "balloonText": "År " + year + ": [[value]]",
                "valueField": year,
                "fillAlphas": 0.8,
                "lineAlpha": 0.2,
                "type": "column",
                "labelText": "[[value]]",
                "lineColor": colors[year]
            }
        });

        AmCharts.makeChart(id, {
            "rotate": true,
            "type": "serial",
            "startDuration": 0,
            "categoryField": "label",
            "categoryAxis": {
                "gridPosition": "start",
                "position": "left"
            },
            "valueAxes": [
                {
                    "integersOnly": true
                }
            ],
            numberFormatter: {
                decimalSeparator: ',',
                thousandsSeparator: ' '
            },
            "legend": {
                "markerSize": 10,
                "position": "top",
                "useGraphSettings": true,
                "switchable": false
            },
            "graphs": graphs,
            "dataProvider": chart
        });
    };

    var clean = function (chart, years) {
        return chart.map(function (entry) {
            Object.keys(entry).filter(function (key) {
                return years.indexOf(key) !== -1;
            }).forEach(function (key) {
                entry[key] = Math.round(entry[key] * 10) / 10;
            });
            return entry;
        });
    };

    return {
        'init': function () {
            $(".chart").each(function () {
                var container = $(this);
                var years = JSON.parse(container.attr('data-years')).sort().reverse();
                var chart = clean(JSON.parse(container.attr('data-chart')), years);

                container.css("height", 250 + 50 * chart.length + "px");
                makeChart(container.attr("id"), years, chart)
            });
        }
    }
});