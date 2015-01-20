define(['jquery', 'amcharts.theme'], function($, AmCharts) {
    var makeChart = function(id, years, chart) {
        var yearColors = { };
        var colors = ["#53bafa", "#2caf43", "#5f0009"];
        for(var i = 0; i < years.length; i++) {
            yearColors[years[i]] = colors[i];
        }

        var graphs = $.map(years, function(year) {
            return {
                "id": "graph-" + year,
                "title": "År " + year,
                "balloonText": "År " + year + ": [[value]]",
                "valueField": year,
                "fillAlphas": 0.8,
                "lineAlpha": 0.2,
                "type": "column",
                "labelText": "[[value]]",
                "lineColor": yearColors[year]
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

    var round = function(n) {
        return Math.round(n * 10) / 10;
    };

    var clean = function(n) {
        if(n !== Math.round(n)) {
            return n;
        }

        return Math.round(n);
    };

    var cleanupChart = function(chart, years) {
        for(var i = 0; i < chart.length; i++) {
            var entry = chart[i];

            for(var j = 0; j < years.length; j++) {
                var year = years[j];

                if(entry.hasOwnProperty(year)) {
                    entry[year] = clean(round(entry[year]));
                }
            }
        }
    };

    return {
        'init': function() {
            $(".chart").each(function() {
                var container = $(this);

                var years = JSON.parse(container.attr('data-years'));
                years.sort();
                years.reverse();

                var chart = JSON.parse(container.attr('data-chart'));
                cleanupChart(chart, years);

                container.css("height", 250 + 50 * chart.length + "px");

                makeChart(container.attr("id"), years, chart)
            });
        }
    }
});