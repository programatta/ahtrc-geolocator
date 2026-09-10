var MapData = {
    literaryWorksData:[],

    addData:function(data){
        this.literaryWorksData.push(data)
    }
};


function _corePage(literaryWorksData){
    // Inicializar el mapa
    const map = L.map('map',{
        maxZoom:7, //6
        minZoom:1,
        maxBounds: L.latLngBounds([-90, -180], [90, 180]),
        maxBoundsViscosity: 1.0,
    }).setView([40.4167, -3.7037], 6); // Vista inicial (España); si hay obras, renderMarkers() la ajusta con fitBounds.
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        noWrap: true,
    }).addTo(map);

    //let markersLayer = L.layerGroup().addTo(map);
    let markersCluster = L.markerClusterGroup({
        //chunkedLoading: true,
        showCoverageOnHover: false, // Opcional: no muestra el área que abarca el cluster
        zoomToBoundsOnClick: true,  // Al hacer click, hace zoom hasta que se separan
        spiderfyOnMaxZoom: true,     // Si están en la misma coordenada exacta, los separa en abanico
        //disableClusteringAtZoom: 9 //7
    });
    
    map.addLayer(markersCluster);

    const defaultIcon = new L.Icon.Default();
    const selectedIcon = new L.Icon.Default({ className: 'marker-icon-selected' });

    let selectedMarker = null;

    function selectMarker(marker) {
        if (selectedMarker && selectedMarker !== marker) {
            selectedMarker.setIcon(defaultIcon);
            selectedMarker.setZIndexOffset(0);
        }
        marker.setIcon(selectedIcon);
        marker.setZIndexOffset(1000);
        selectedMarker = marker;
    }

    function deselectMarker() {
        if (selectedMarker) {
            selectedMarker.setIcon(defaultIcon);
            selectedMarker.setZIndexOffset(0);
            selectedMarker = null;
        }
    }


    //--- Otras funciones.
    function renderMarkers(works) {
        closeDrawer();
        markersCluster.clearLayers();
        works.forEach(function (work) {
            const marker = L.marker([work.lat, work.lng], { icon: defaultIcon });
            marker.on('click', function () {
                selectMarker(marker);
                openDrawer(work);
            });
            markersCluster.addLayer(marker);
        });
        if (markersCluster.getLayers().length > 0) {
            map.fitBounds(markersCluster.getBounds());
        }
    }

    //-------------------------------------------------------------------------
    // -- Funcionalidad del Drawer.
    //-------------------------------------------------------------------------
    const workDrawer = document.getElementById('work-drawer');
    const workDrawerBackdrop = document.getElementById('work-drawer-backdrop');

    function openDrawer(work) {
        document.getElementById('work-drawer-title').textContent = work.title;
        document.getElementById('work-drawer-author').textContent = work.authorName;
        document.getElementById('work-drawer-classic-author').textContent = work.classicAuthorName;
        document.getElementById('work-drawer-genre').textContent = work.genreName;
        document.getElementById('work-drawer-description').textContent = work.description;
        document.getElementById('description-section').style.display = work.description ? "block" : "none";

        document.getElementById('links-section').style.display=(work.links.length>0) ? "block" : "none";
        const linksList = document.getElementById('work-drawer-links');
        linksList.innerHTML = '';
        work.links.forEach(function (url) {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = url;
            item.appendChild(link);
            linksList.appendChild(item);
        });

        document.getElementById('images-section').style.display= (work.images.length>0) ? "block" : "none";
        renderCarouselImages(work.images);

        workDrawer.classList.add('open');
        workDrawerBackdrop.classList.add('open');
    }

    const imagesCarousel = document.getElementById('work-drawer-images-carousel');
    const imagesTrack = document.getElementById('work-drawer-images');
    const imagesPrevButton = document.getElementById('work-drawer-images-prev');
    const imagesNextButton = document.getElementById('work-drawer-images-next');
    let carouselImageCount = 0;
    let carouselIndex = 0;

    function renderCarouselImages(images) {
        imagesTrack.innerHTML = '';
        images.forEach(function (url) {
            const item = document.createElement('li');
            const image = document.createElement('img');
            image.src = url;
            item.appendChild(image);
            imagesTrack.appendChild(item);
        });
        carouselImageCount = images.length;
        carouselIndex = 0;
        imagesCarousel.classList.toggle('image-carousel--collapsed', carouselImageCount <= 1);
        updateCarouselPosition();
    }

    function updateCarouselPosition() {
        imagesTrack.style.setProperty('--pos', `-${carouselIndex * 100}%`);
        imagesPrevButton.disabled = carouselIndex === 0;
        imagesNextButton.disabled = carouselIndex >= carouselImageCount - 1;
    }

    function bounceCarousel(direction) {
        const bounceClass = direction === 'prev' ? 'bounce-left' : 'bounce-right';
        imagesTrack.classList.remove('bounce-left', 'bounce-right');
        void imagesTrack.offsetWidth; // fuerza el reflow para poder repetir la animación
        imagesTrack.classList.add(bounceClass);
    }

    imagesTrack.addEventListener('animationend', function () {
        imagesTrack.classList.remove('bounce-left', 'bounce-right');
    });

    imagesPrevButton.addEventListener('click', function () {
        if (carouselIndex === 0) {
            bounceCarousel('prev');
            return;
        }
        carouselIndex -= 1;
        updateCarouselPosition();
    });

    imagesNextButton.addEventListener('click', function () {
        if (carouselIndex >= carouselImageCount - 1) {
            bounceCarousel('next');
            return;
        }
        carouselIndex += 1;
        updateCarouselPosition();
    });

    function closeDrawer() {
        workDrawer.classList.remove('open');
        workDrawerBackdrop.classList.remove('open');
        deselectMarker();
    }

    document.getElementById('work-drawer-close-icon').addEventListener('click', closeDrawer);
    document.getElementById('work-drawer-close-button').addEventListener('click', closeDrawer);
    workDrawerBackdrop.addEventListener('click', closeDrawer);

    //-------------------------------------------------------------------------
    //--- Funcion que alimenta el mapa.
    //-------------------------------------------------------------------------
    renderMarkers(literaryWorksData);


    //-------------------------------------------------------------------------
     // -- Controles: filtros y boton de restablecimiento del mapa.
    //-------------------------------------------------------------------------
    const classicAuthorSelect = document.getElementById('classic-author-select');
    const authorSelect = document.getElementById('author-select');

    function worksForClassicAuthor(classicAuthorId) {
        if (!classicAuthorId) {
            return literaryWorksData;
        }
        return literaryWorksData.filter(function (work) {
            return String(work.classicAuthorId) === classicAuthorId;
        });
    }

    function resetAuthorSelect() {
        authorSelect.innerHTML = '<option value="" selected disabled>--Seleccione un autor--</option>';
        authorSelect.disabled = true;
    }

    function populateAuthorSelect(works) {
        const authorsById = new Map();
        works.forEach(function (work) {
            if (!authorsById.has(work.authorId)) {
                authorsById.set(work.authorId, work.authorName);
            }
        });
        const authors = Array.from(authorsById.entries()).sort(function (a, b) {
            return a[1].localeCompare(b[1]);
        });

        resetAuthorSelect();
        authors.forEach(function (entry) {
            const option = document.createElement('option');
            option.value = entry[0];
            option.textContent = entry[1];
            authorSelect.appendChild(option);
        });
        authorSelect.disabled = false;
    }

    classicAuthorSelect.addEventListener('change', function () {
        const works = worksForClassicAuthor(this.value);
        renderMarkers(works);
        if (this.value) {
            populateAuthorSelect(works);
        } else {
            resetAuthorSelect();
        }
    });

    authorSelect.addEventListener('change', function () {
        const works = worksForClassicAuthor(classicAuthorSelect.value);
        if (!this.value) {
            renderMarkers(works);
            return;
        }
        renderMarkers(works.filter(function (work) {
            return String(work.authorId) === this.value;
        }, this));
    });

    document.getElementById('reset-filters-button').addEventListener('click', function () {
        classicAuthorSelect.selectedIndex = 0;
        resetAuthorSelect();
        renderMarkers(literaryWorksData);
    });
}
