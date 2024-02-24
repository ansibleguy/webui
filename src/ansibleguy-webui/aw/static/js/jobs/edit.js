function getRepositoryToBrowse() {
    let selectedRepository = document.getElementById('id_repository').value;
    document.getElementById('id_playbook_file').setAttribute("aw-fs-repository", selectedRepository);
    document.getElementById('id_inventory_file').setAttribute("aw-fs-repository", selectedRepository);
}

$( document ).ready(function() {
    getRepositoryToBrowse();
    setInterval('getRepositoryToBrowse()', (DATA_REFRESH_SEC * 1000));
});
