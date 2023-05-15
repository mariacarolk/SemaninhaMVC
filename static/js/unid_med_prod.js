$(function(){

  function unid_med_change(){
    var id_preparo = $("#preparo").val();
    var url_format = "/unid_med/" + id_preparo + "/" + 2

    $.ajax({
      type: "GET",
      url: url_format
    }).done(function(data){
      $("#unidade_medida").attr("value", data.unidade_medida[1])
      $("#unidade_medida").prop("readonly", true);
    });
  }

  $("#preparo").change(function(){
    unid_med_change();
  });

  unid_med_change();
});
