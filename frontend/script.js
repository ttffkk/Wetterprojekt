const { createApp, ref, onMounted, watch } = Vue;

        createApp({
            setup() {
                const map = ref(null);
                const allStations = ref([]);
                const stationMarkers = ref(null);
                const showStations = ref(false);
                const searchQuery = ref('');
                const filteredStations = ref([]);
                const searchFocused = ref(false);

                const liveWeather = ref({});
                const nearestStations = ref([]);
                const selectedStation = ref({});

                const analysisParams = ref({
                    start_date: '',
                    end_date: '',
                    metric: 'tmk',
                    aggregation: 'monthly',
                });

                const chartData = ref({ labels: [], values: [] });
                const historicalData = ref({ rows: [] });
                let clickMarker = null;

                // --- Map Initialization ---
                onMounted(() => {
                    map.value = L.map('map').setView([51.16, 10.45], 6);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 18,
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    }).addTo(map.value);

                    stationMarkers.value = L.layerGroup();

                    fetchAllStations();

                    map.value.on('click', onMapClick);
                });

                // --- API Calls ---
                const fetchAllStations = async () => {
                    try {
                        const response = await fetch('/api/all_stations');
                        const data = await response.json();
                        allStations.value = data.stations.map(s => ({
                            station_id: s.station_id,
                            station_name: s.station_name,
                            latitude: s.latitude,
                            longitude: s.longitude,
                            start_date: s.start_date.substring(0, 10),
                            end_date: s.end_date.substring(0, 10),
                        }));
                    } catch (error) {
                        console.error("Failed to fetch stations:", error);
                    }
                };

                const fetchLiveWeather = async (lat, lon) => {
                    try {
                        const response = await fetch(`/api/live_weather?lat=${lat}&lon=${lon}`);
                        liveWeather.value = await response.json();
                    } catch (error) {
                        console.error("Failed to fetch live weather:", error);
                    }
                };

                const fetchNearestStations = async (lat, lon) => {
                    try {
                        const response = await fetch(`/api/nearest_stations?lat=${lat}&lon=${lon}`);
                        const data = await response.json();
                        nearestStations.value = data.stations;
                    } catch (error) {
                        console.error("Failed to fetch nearest stations:", error);
                    }
                };

                const runAnalysis = async () => {
                    if (!selectedStation.value.station_id) return;

                    const params = new URLSearchParams({
                        station_id: selectedStation.value.station_id,
                        start_date: analysisParams.value.start_date,
                        end_date: analysisParams.value.end_date,
                        metric: analysisParams.value.metric,
                        aggregation: analysisParams.value.aggregation
                    });

                    // Fetch chart data
                    try {
                        const response = await fetch(`/api/chart_data?${params.toString()}`);
                        const data = await response.json();
                        chartData.value.labels = data.rows.map(r => r.period);
                        chartData.value.values = data.rows.map(r => r.value);
                        plotChart(data.metric_label);
                    } catch (error) {
                        console.error("Failed to fetch chart data:", error);
                    }

                    // Fetch historical table data
                    const histParams = new URLSearchParams({
                        station_id: selectedStation.value.station_id,
                        start_date: analysisParams.value.start_date,
                        end_date: analysisParams.value.end_date,
                        aggregation: analysisParams.value.aggregation
                    });
                    try {
                        const response = await fetch(`/api/historical_data?${histParams.toString()}`);
                        const data = await response.json();
                        historicalData.value.rows = data.rows;
                    } catch (error) {
                        console.error("Failed to fetch historical data:", error);
                    }
                };

                // --- Map and Station Logic ---
                const updateStationMarkers = () => {
                    stationMarkers.value.clearLayers();
                    if (showStations.value) {
                        allStations.value.forEach(station => {
                            const marker = L.marker([station.latitude, station.longitude]);
                            marker.bindPopup(createPopupContent(station), { className: 'station-popup' });
                            stationMarkers.value.addLayer(marker);
                        });
                        stationMarkers.value.addTo(map.value);
                    } else {
                        map.value.removeLayer(stationMarkers.value);
                    }
                };

                const createPopupContent = (station) => {
                    const container = document.createElement('div');
                    container.innerHTML = `<b>${station.station_name}</b><br>`;
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-primary btn-sm mt-2';
                    btn.innerText = 'Select this station';
                    btn.onclick = () => selectStation(station);
                    container.appendChild(btn);
                    return container;
                };

                const onMapClick = (e) => {
                    const { lat, lng } = e.latlng;
                    fetchLiveWeather(lat, lng);
                    fetchNearestStations(lat, lng);

                    if (clickMarker) {
                        clickMarker.setLatLng(e.latlng);
                    } else {
                        clickMarker = L.marker(e.latlng).addTo(map.value);
                    }
                    clickMarker.bindPopup(`Clicked at ${lat.toFixed(4)}, ${lng.toFixed(4)}`).openPopup();
                };

                const selectStation = (station) => {
                    selectedStation.value = station;
                    map.value.setView([station.latitude, station.longitude], 10);
                    map.value.closePopup();
                    analysisParams.value.start_date = station.start_date;
                    analysisParams.value.end_date = station.end_date;
                };

                const filterStations = () => {
                    if (searchQuery.value.length < 2) {
                        filteredStations.value = [];
                        return;
                    }
                    const lowerQuery = searchQuery.value.toLowerCase();
                    filteredStations.value = allStations.value.filter(s =>
                        s.station_name.toLowerCase().includes(lowerQuery) ||
                        s.station_id.toString().includes(lowerQuery)
                    );
                };

                const hideAutocomplete = () => {
                    // Delay hiding to allow click event to register
                    setTimeout(() => searchFocused.value = false, 200);
                };

                // --- Charting ---
                const plotChart = (metricLabel) => {
                    const trace = {
                        x: chartData.value.labels,
                        y: chartData.value.values,
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: {
                            color: '#4A90E2',
                            width: 2
                        },
                        marker: {
                            color: '#4A90E2',
                            size: 6
                        }
                    };

                    const layout = {
                        title: `${metricLabel} for ${selectedStation.value.station_name}`,
                        xaxis: { title: 'Period' },
                        yaxis: { title: metricLabel },
                        margin: { t: 40, l: 60, r: 20, b: 50 },
                        paper_bgcolor: 'transparent',
                        plot_bgcolor: 'transparent',
                        font: {
                            family: 'Inter, sans-serif'
                        }
                    };

                    Plotly.newPlot('chart', [trace], layout, { responsive: true });
                };

                // --- Watchers ---
                watch(showStations, updateStationMarkers);

                // --- Helpers ---
                const formatTimestamp = (ts) => ts ? new Date(ts).toLocaleString() : 'N/A';

                return {
                    showStations,
                    searchQuery,
                    filteredStations,
                    searchFocused,
                    liveWeather,
                    nearestStations,
                    selectedStation,
                    analysisParams,
                    chartData,
                    historicalData,
                    filterStations,
                    hideAutocomplete,
                    selectStation,
                    runAnalysis,
                    formatTimestamp,
                };
            }
        }).mount('#app');